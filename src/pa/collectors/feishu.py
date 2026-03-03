"""飞书多维表格采集器."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from pa.collectors.base import BaseCollector


class FeishuAuthError(Exception):
    """飞书认证错误."""

    pass


class FeishuAPIError(Exception):
    """飞书 API 错误."""

    pass


class FeishuCollector(BaseCollector):
    """飞书多维表格数据采集器."""

    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(
        self,
        name: str,
        raw_dir: Path,
        app_id: str,
        app_secret: str,
        app_token: str,
        table_id: str,
        field_mapping: dict[str, str] | None = None,
    ) -> None:
        super().__init__(name, raw_dir)
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.table_id = table_id
        self.field_mapping = field_mapping or {
            "title": "标题",
            "content": "内容",
            "tags": "标签",
            "created_time": "创建时间",
        }
        self._access_token: str | None = None
        self._token_expire: datetime | None = None

    def get_source_type(self) -> str:
        return "feishu_bitable"

    async def _get_access_token(self) -> str:
        """获取 tenant access token."""
        if self._access_token and self._token_expire and datetime.now() < self._token_expire:
            return self._access_token

        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()

            if result.get("code") != 0:
                raise FeishuAuthError(f"获取 access token 失败: {result}")

            self._access_token = result["tenant_access_token"]
            # Token 有效期 2 小时，提前 5 分钟刷新
            expire_in = result.get("expire", 7200)
            self._token_expire = datetime.now().timestamp() + expire_in - 300

            return self._access_token

    def _get_headers(self) -> dict[str, str]:
        """获取请求头."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    async def _fetch_records(self) -> list[dict[str, Any]]:
        """获取多维表格记录."""
        token = await self._get_access_token()
        url = f"{self.BASE_URL}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        headers = {"Authorization": f"Bearer {token}"}

        all_records: list[dict[str, Any]] = []
        page_token: str | None = None

        async with httpx.AsyncClient() as client:
            while True:
                params: dict[str, Any] = {"page_size": 500}
                if page_token:
                    params["page_token"] = page_token

                response = await client.get(url, headers=headers, params=params)
                result = response.json()

                if result.get("code") != 0:
                    raise FeishuAPIError(f"获取记录失败: {result}")

                data = result.get("data", {})
                items = data.get("items", [])
                all_records.extend(items)

                # 处理附件字段的 file_token
                for record in items:
                    fields = record.get("fields", {})
                    for field_name, field_value in fields.items():
                        if isinstance(field_value, list) and field_value:
                            # 检查是否是附件类型
                            if field_value[0].get("type") == "file":
                                file_tokens = [
                                    f["file_token"]
                                    for f in field_value
                                    if "file_token" in f
                                ]
                                if file_tokens:
                                    # 批量获取下载 URL
                                    urls = await self._batch_get_download_urls(
                                        client, headers, file_tokens
                                    )
                                    # 替换为实际 URL
                                    for f, url in zip(field_value, urls):
                                        f["tmp_download_url"] = url

                if not data.get("has_more"):
                    break
                page_token = data.get("page_token")

                # 避免触发限流
                await asyncio.sleep(0.1)

        return all_records

    async def _batch_get_download_urls(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str],
        file_tokens: list[str],
    ) -> list[str]:
        """批量获取文件下载 URL.

        根据经验，每批处理 5 个，批次间延迟 500ms 避免限流
        """
        url = f"{self.BASE_URL}/drive/v1/files/batch_get_tmp_download_url"
        result_urls: list[str] = []

        # 分批处理，每批 5 个
        batch_size = 5
        for i in range(0, len(file_tokens), batch_size):
            batch = file_tokens[i : i + batch_size]

            # 构建参数：每个 token 作为单独的 file_tokens 参数
            params = [("file_tokens", token) for token in batch]

            response = await client.get(url, headers=headers, params=params)
            result = response.json()

            if result.get("code") != 0:
                # 如果失败，返回空字符串占位
                result_urls.extend([""] * len(batch))
                continue

            # 构建 token -> url 映射
            url_map = {
                item["file_token"]: item.get("tmp_download_url", "")
                for item in result.get("data", {}).get("tmp_download_urls", [])
            }

            # 按原顺序返回
            for token in batch:
                result_urls.append(url_map.get(token, ""))

            # 批次间延迟，避免限流
            if i + batch_size < len(file_tokens):
                await asyncio.sleep(0.5)

        return result_urls

    def _normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """标准化记录格式."""
        fields = record.get("fields", {})
        record_id = record.get("record_id", "")

        # 根据字段映射提取内容
        normalized: dict[str, Any] = {
            "id": record_id,
            "source": self.name,
            "source_type": self.get_source_type(),
        }

        # 提取标题
        title_field = self.field_mapping.get("title", "标题")
        title_value = fields.get(title_field, "")
        if isinstance(title_value, list):
            title_value = title_value[0].get("text", "") if title_value else ""
        normalized["title"] = str(title_value) if title_value else "无标题"

        # 提取内容
        content_field = self.field_mapping.get("content", "内容")
        content_value = fields.get(content_field, "")
        if isinstance(content_value, list):
            # 富文本类型
            content_parts = []
            for item in content_value:
                if "text" in item:
                    content_parts.append(item["text"])
            normalized["content"] = "".join(content_parts)
        else:
            normalized["content"] = str(content_value) if content_value else ""

        # 提取标签
        tags_field = self.field_mapping.get("tags", "标签")
        tags_value = fields.get(tags_field, [])
        if isinstance(tags_value, list):
            normalized["tags"] = [str(t) for t in tags_value]
        else:
            normalized["tags"] = [str(tags_value)] if tags_value else []

        # 提取创建时间
        created_field = self.field_mapping.get("created_time", "创建时间")
        created_value = fields.get(created_field)
        if created_value:
            normalized["created_time"] = created_value
        else:
            normalized["created_time"] = record.get("created_time", datetime.now().isoformat())

        # 保留原始所有字段
        normalized["raw_fields"] = fields

        return normalized

    async def collect(self) -> list[dict[str, Any]]:
        """执行采集."""
        records = await self._fetch_records()
        normalized = [self._normalize_record(r) for r in records]
        self.save_raw(normalized)
        return normalized
