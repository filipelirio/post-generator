import base64
import mimetypes
import time
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import requests

from app.core.config import settings


class WordPressClient:
    def __init__(self) -> None:
        self.base_url = settings.WORDPRESS_URL.rstrip("/")
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.username = settings.WORDPRESS_USERNAME
        self.password = settings.WORDPRESS_APPLICATION_PASSWORD
        self.request_timeout = 15
        self.request_retries = 3
        self.retry_delay = 5

    def _auth_token(self) -> str:
        auth_string = f"{self.username}:{self.password}"
        return base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

    def _headers(self, content_type: str = "application/json") -> Dict[str, str]:
        if not self.username or not self.password:
            return {}
        return {
            "Authorization": f"Basic {self._auth_token()}",
            "Content-Type": content_type,
            "User-Agent": "EasyMedicinaLocalAutomation/1.0",
            "Accept": "application/json",
        }

    def _api(self, endpoint: str) -> str:
        return f"{self.api_url}/{endpoint.lstrip('/')}"

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        last_error: Optional[Exception] = None
        headers = kwargs.pop("headers", self._headers())
        url = self._api(endpoint)

        for attempt in range(1, self.request_retries + 1):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self.request_timeout,
                    **kwargs,
                )
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt < self.request_retries:
                    time.sleep(self.retry_delay)

        raise Exception(f"Erro ao acessar WordPress em {url}: {last_error}")

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        normalized = normalized.strip().lower().replace("&", " e ")
        out = []
        prev_dash = False
        for char in normalized:
            if char.isalnum():
                out.append(char)
                prev_dash = False
            elif not prev_dash:
                out.append("-")
                prev_dash = True
        slug = "".join(out).strip("-")
        return slug or "categoria"

    def test_connection(self) -> bool:
        try:
            response = self._request("GET", "users/me")
            return response.status_code == 200
        except Exception:
            return False

    def get_posts(self, status: str = "draft", per_page: int = 20) -> List[Dict[str, Any]]:
        params = {"per_page": per_page}
        if status and status != "any":
            params["status"] = status
        response = self._request("GET", "posts", params=params)
        return response.json()

    def get_post(self, post_id: int) -> Dict[str, Any]:
        response = self._request("GET", f"posts/{post_id}")
        return response.json()

    def get_post_by_slug(self, slug: str, status: str = "any") -> Optional[Dict[str, Any]]:
        params: Dict[str, Any] = {"slug": slug}
        if status and status != "any":
            params["status"] = status
        response = self._request("GET", "posts", params=params)
        posts = response.json()
        return posts[0] if posts else None

    def get_post_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        if not url:
            return None

        parsed = urlparse(url)
        query_post_id = parse_qs(parsed.query).get("p", [])
        if query_post_id:
            try:
                return self.get_post(int(query_post_id[0]))
            except Exception:
                return None

        slug = parsed.path.rstrip("/").split("/")[-1].strip()
        if not slug:
            return None

        try:
            return self.get_post_by_slug(slug, status="any")
        except Exception:
            return None

    def update_post(self, post_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self._request("POST", f"posts/{post_id}", json=payload)
        return response.json()

    def create_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self._request("POST", "posts", json=post_data)
        return response.json()

    def get_categories(self) -> List[Dict[str, Any]]:
        response = self._request("GET", "categories", params={"per_page": 100})
        return response.json()

    def get_tags(self) -> List[Dict[str, Any]]:
        response = self._request("GET", "tags", params={"per_page": 100})
        return response.json()

    def create_category(self, name: str, slug: Optional[str] = None) -> int:
        payload: Dict[str, Any] = {"name": name}
        if slug:
            payload["slug"] = slug
        response = self._request("POST", "categories", json=payload)
        return response.json()["id"]

    def create_tag(self, name: str) -> int:
        response = self._request("POST", "tags", json={"name": name})
        return response.json()["id"]

    def get_or_create_category(self, name: str) -> Optional[int]:
        if not name:
            return None
        slug = self._slugify(name)
        response = self._request("GET", "categories", params={"slug": slug})
        categories = response.json()
        if categories:
            return categories[0]["id"]

        all_categories = self.get_categories()
        for category in all_categories:
            if category["name"].strip().lower() == name.strip().lower():
                return category["id"]

        return self.create_category(name=name, slug=slug)

    def get_or_create_tag(self, name: str) -> Optional[int]:
        if not name:
            return None
        response = self._request("GET", "tags", params={"search": name})
        for tag in response.json():
            if tag["name"].strip().lower() == name.strip().lower():
                return tag["id"]
        return self.create_tag(name)

    def update_yoast(
        self,
        post_id: int,
        seo_title: str = "",
        meta_desc: str = "",
        focus_kw: str = "",
        canonical: str = "",
        og_title: str = "",
        og_desc: str = "",
        og_image_url: str = "",
        twitter_title: str = "",
        twitter_desc: str = "",
        twitter_image_url: str = "",
        schema_article_type: str = "Article",
        schema_page_type: str = "WebPage",
        is_cornerstone: bool = False,
        robots_noindex: bool = False,
        robots_nofollow: bool = False,
    ) -> Dict[str, Any]:
        meta: Dict[str, Any] = {}

        if seo_title:
            meta["_yoast_wpseo_title"] = seo_title
        if meta_desc:
            meta["_yoast_wpseo_metadesc"] = meta_desc
        if focus_kw:
            meta["_yoast_wpseo_focuskw"] = focus_kw
        if canonical:
            meta["_yoast_wpseo_canonical"] = canonical
        if og_title:
            meta["_yoast_wpseo_opengraph-title"] = og_title
        if og_desc:
            meta["_yoast_wpseo_opengraph-description"] = og_desc
        if og_image_url:
            meta["_yoast_wpseo_opengraph-image"] = og_image_url
        if twitter_title:
            meta["_yoast_wpseo_twitter-title"] = twitter_title
        if twitter_desc:
            meta["_yoast_wpseo_twitter-description"] = twitter_desc
        if twitter_image_url:
            meta["_yoast_wpseo_twitter-image"] = twitter_image_url
        if schema_article_type:
            meta["_yoast_wpseo_schema_article_type"] = schema_article_type
        if schema_page_type:
            meta["_yoast_wpseo_schema_page_type"] = schema_page_type

        meta["_yoast_wpseo_is_cornerstone"] = "1" if is_cornerstone else "0"
        if robots_noindex:
            meta["_yoast_wpseo_meta-robots-noindex"] = "1"
        if robots_nofollow:
            meta["_yoast_wpseo_meta-robots-nofollow"] = "1"

        if not meta:
            return {}

        response = self._request("POST", f"posts/{post_id}", json={"meta": meta})
        return response.json()

    def upload_media(self, file_bytes: bytes, filename: str, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        headers = self._headers(content_type=mime_type)
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        response = self._request("POST", "media", headers=headers, data=file_bytes)
        return response.json()

    def upload_media_from_path(self, path: str) -> Dict[str, Any]:
        local_path = Path(path)
        if not local_path.exists():
            raise FileNotFoundError(f"Arquivo de imagem nao encontrado: {path}")
        mime_type = mimetypes.guess_type(local_path.name)[0] or "image/jpeg"
        return self.upload_media(local_path.read_bytes(), local_path.name, mime_type)

    def upload_media_from_url(self, url: str) -> Dict[str, Any]:
        response = requests.get(url, timeout=self.request_timeout)
        response.raise_for_status()
        filename = url.split("/")[-1].split("?")[0] or "capa.jpg"
        mime_type = response.headers.get("Content-Type", "image/jpeg").split(";")[0]
        return self.upload_media(response.content, filename, mime_type)

    def set_featured_media(self, post_id: int, media_id: int) -> Dict[str, Any]:
        response = self._request("POST", f"posts/{post_id}", json={"featured_media": media_id})
        return response.json()


wordpress_client = WordPressClient()
