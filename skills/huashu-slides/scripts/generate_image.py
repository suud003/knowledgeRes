#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "zhipuai>=2.0.0",
#     "pillow>=10.0.0",
#     "httpx[socks]",
# ]
# ///
"""
Generate images using multiple AI providers (GLM CogView or Gemini).

Usage:
    # Using GLM (default if ZHIPUAI_API_KEY is set)
    uv run generate_image.py --prompt "描述" --filename "output.png" --provider glm

    # Using Gemini
    uv run generate_image.py --prompt "description" --filename "output.png" --provider gemini

    # Auto-detect provider based on available API keys
    uv run generate_image.py --prompt "description" --filename "output.png"

Supported Providers:
    - glm: 智谱 CogView-4 (recommended for Chinese prompts)
    - gemini: Google Gemini 3 Pro Image
"""

import argparse
import os
import sys
from pathlib import Path
from io import BytesIO


def get_api_key(provider: str, provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    
    env_vars = {
        "glm": "ZHIPUAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }
    return os.environ.get(env_vars.get(provider, ""))


def detect_provider() -> str | None:
    """Auto-detect available provider based on environment variables."""
    if os.environ.get("ZHIPUAI_API_KEY"):
        return "glm"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    return None


def generate_with_glm(prompt: str, output_path: Path, api_key: str, size: str = "1024x1024", model: str = "glm-image") -> bool:
    """Generate image using 智谱 GLM-Image / CogView."""
    from zhipuai import ZhipuAI
    import httpx
    from PIL import Image as PILImage
    
    client = ZhipuAI(api_key=api_key)
    
    print(f"Using {model}, size: {size}...")
    
    try:
        response = client.images.generations(
            model=model,  # glm-image 或 cogview-4
            prompt=prompt,
            size=size,
        )
        
        # CogView 返回图片 URL
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            print(f"Image generated, downloading...")
            
            # 下载图片
            with httpx.Client() as http_client:
                img_response = http_client.get(image_url)
                img_response.raise_for_status()
                
                image = PILImage.open(BytesIO(img_response.content))
                
                # 转换并保存为 PNG
                if image.mode == 'RGBA':
                    rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    rgb_image.save(str(output_path), 'PNG')
                elif image.mode == 'RGB':
                    image.save(str(output_path), 'PNG')
                else:
                    image.convert('RGB').save(str(output_path), 'PNG')
                
                return True
        
        print("Error: No image URL in response", file=sys.stderr)
        return False
        
    except Exception as e:
        print(f"GLM generation error: {e}", file=sys.stderr)
        return False


def generate_with_gemini(prompt: str, output_path: Path, api_key: str, 
                         resolution: str = "1K", input_image_path: str | None = None) -> bool:
    """Generate image using Google Gemini 3 Pro Image."""
    from google import genai
    from google.genai import types
    from PIL import Image as PILImage
    
    client = genai.Client(api_key=api_key)
    
    # Load input image if provided
    input_image = None
    output_resolution = resolution
    
    if input_image_path:
        try:
            input_image = PILImage.open(input_image_path)
            print(f"Loaded input image: {input_image_path}")
            
            # Auto-detect resolution
            if resolution == "1K":
                width, height = input_image.size
                max_dim = max(width, height)
                if max_dim >= 3000:
                    output_resolution = "4K"
                elif max_dim >= 1500:
                    output_resolution = "2K"
                else:
                    output_resolution = "1K"
                print(f"Auto-detected resolution: {output_resolution}")
        except Exception as e:
            print(f"Error loading input image: {e}", file=sys.stderr)
            return False
    
    # Build contents
    if input_image:
        contents = [input_image, prompt]
        print(f"Editing image with Gemini, resolution {output_resolution}...")
    else:
        contents = prompt
        print(f"Generating image with Gemini, resolution {output_resolution}...")
    
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    image_size=output_resolution
                )
            )
        )
        
        image_saved = False
        for part in response.parts:
            if part.text is not None:
                print(f"Model response: {part.text}")
            elif part.inline_data is not None:
                import base64
                
                image_data = part.inline_data.data
                if isinstance(image_data, str):
                    image_data = base64.b64decode(image_data)
                
                image = PILImage.open(BytesIO(image_data))
                
                if image.mode == 'RGBA':
                    rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    rgb_image.save(str(output_path), 'PNG')
                elif image.mode == 'RGB':
                    image.save(str(output_path), 'PNG')
                else:
                    image.convert('RGB').save(str(output_path), 'PNG')
                image_saved = True
        
        return image_saved
        
    except Exception as e:
        print(f"Gemini generation error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using GLM CogView or Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect provider
  %(prog)s -p "一只可爱的猫咪" -f cat.png
  
  # Force GLM provider
  %(prog)s -p "山水画风景" -f landscape.png --provider glm
  
  # Use Gemini with high resolution
  %(prog)s -p "Abstract art" -f art.png --provider gemini -r 2K
  
  # Edit existing image (Gemini only)
  %(prog)s -p "Add rainbow" -f edited.png --provider gemini -i input.png

Environment Variables:
  ZHIPUAI_API_KEY  - API key for GLM CogView
  GEMINI_API_KEY   - API key for Google Gemini
"""
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., output.png)"
    )
    parser.add_argument(
        "--provider",
        choices=["glm", "gemini"],
        help="AI provider (auto-detect if not specified)"
    )
    parser.add_argument(
        "--input-image", "-i",
        help="Input image for editing (Gemini only)"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution for Gemini (default: 1K)"
    )
    parser.add_argument(
        "--size", "-s",
        choices=["1024x1024", "768x1344", "864x1152", "1344x768", "1152x864", "1440x720", "720x1440"],
        default="1024x1024",
        help="Image size for GLM (default: 1024x1024)"
    )
    parser.add_argument(
        "--model", "-m",
        default="glm-image",
        help="GLM model name (default: glm-image, also supports cogview-4)"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="API key (overrides environment variable)"
    )

    args = parser.parse_args()

    # Determine provider
    provider = args.provider or detect_provider()
    
    if not provider:
        print("Error: No provider specified and no API key found.", file=sys.stderr)
        print("\nPlease either:", file=sys.stderr)
        print("  1. Set ZHIPUAI_API_KEY environment variable (for GLM)", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable (for Gemini)", file=sys.stderr)
        print("  3. Use --provider with --api-key arguments", file=sys.stderr)
        sys.exit(1)

    # Get API key
    api_key = get_api_key(provider, args.api_key)
    if not api_key:
        env_var = "ZHIPUAI_API_KEY" if provider == "glm" else "GEMINI_API_KEY"
        print(f"Error: No API key for {provider}.", file=sys.stderr)
        print(f"Please set {env_var} or use --api-key", file=sys.stderr)
        sys.exit(1)

    # Validate input image option
    if args.input_image and provider != "gemini":
        print("Warning: --input-image is only supported with Gemini provider", file=sys.stderr)

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Provider: {provider.upper()}")
    
    # Generate image
    if provider == "glm":
        success = generate_with_glm(args.prompt, output_path, api_key, args.size, args.model)
    else:
        success = generate_with_gemini(
            args.prompt, output_path, api_key, 
            args.resolution, args.input_image
        )

    if success:
        full_path = output_path.resolve()
        print(f"\nImage saved: {full_path}")
    else:
        print("\nImage generation failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
