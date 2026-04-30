from datetime import datetime
from typing import Dict

from app.services.editorial_file_service import editorial_file_service
from app.services.excel_editorial_service import excel_editorial_service
from app.integrations.wordpress import wordpress_client


class EditorialPublishService:
    def _map_wordpress_status(self, wp_status: str) -> str:
        normalized = (wp_status or "").strip().lower()
        if normalized == "publish":
            return "Publicado"
        if normalized in {"draft", "pending", "future", "private"}:
            return "Rascunho"
        return "Rascunho"

    def _category_ids(self, category_name: str) -> list[int]:
        if not category_name:
            return []
        try:
            category_id = wordpress_client.get_or_create_category(category_name)
            return [category_id] if category_id else []
        except Exception:
            return []

    def _tag_ids(self, tags: list[str]) -> list[int]:
        tag_ids = []
        for tag in tags:
            try:
                tag_id = wordpress_client.get_or_create_tag(tag)
                if tag_id:
                    tag_ids.append(tag_id)
            except Exception:
                continue
        return tag_ids

    def _attach_featured_image(self, post_id: int, package: Dict) -> Dict:
        image = package.get("image", {}) or {}
        image_url = image.get("url", "").strip()
        image_path = image.get("path", "").strip()

        if image_url:
            media = wordpress_client.upload_media_from_url(image_url)
            wordpress_client.set_featured_media(post_id, media["id"])
            return {"status": "adicionada", "media_id": media["id"], "source": "url"}

        if image_path:
            media = wordpress_client.upload_media_from_path(image_path)
            wordpress_client.set_featured_media(post_id, media["id"])
            return {"status": "adicionada", "media_id": media["id"], "source": "path"}

        return {"status": "sem imagem"}

    def _resolve_slug(self, slug: str | None = None, pauta_id: str | None = None) -> str:
        if pauta_id:
            return editorial_file_service.find_slug_by_pauta_id(str(pauta_id))
        if slug:
            return slug
        raise ValueError("slug ou pauta_id sao obrigatorios para publicar")

    def publish(self, slug: str | None = None, publish_status: str = "draft", pauta_id: str | None = None) -> Dict:
        slug = self._resolve_slug(slug=slug, pauta_id=pauta_id)
        package = editorial_file_service.load_package(slug)

        post_data = {
            "title": package["title"],
            "content": package["content_html"],
            "slug": package["slug"],
            "excerpt": package["meta_desc"],
            "status": publish_status,
            "categories": self._category_ids(package["category"]),
            "tags": self._tag_ids(package["tags"]),
        }

        response = wordpress_client.create_post(post_data)
        post_id = response.get("id")
        link = response.get("link", "")

        try:
            wordpress_client.update_yoast(
                post_id=post_id,
                seo_title=package["seo_title"] or package["title"],
                meta_desc=package["meta_desc"],
                focus_kw=package["focus_kw"],
                canonical=link,
                og_title=package["seo_title"] or package["title"],
                og_desc=package["meta_desc"],
                twitter_title=package["seo_title"] or package["title"],
                twitter_desc=package["meta_desc"],
                schema_article_type="Article",
                schema_page_type="WebPage",
            )
        except Exception:
            pass

        try:
            image_result = self._attach_featured_image(post_id, package)
        except Exception:
            image_result = {"status": "falhou"}

        resolved_pauta_id = package.get("pauta_id") or pauta_id
        if resolved_pauta_id:
            excel_editorial_service.update_row(
                str(resolved_pauta_id),
                {
                    "Status": "Publicado" if publish_status == "publish" else "Rascunho",
                    "Data publicacao": datetime.now().strftime("%Y-%m-%d"),
                    "URL WordPress": response.get("link", ""),
                },
            )

        return {
            "post_id": post_id,
            "url": link,
            "status": publish_status,
            "message": "Post publicado com sucesso" if publish_status == "publish" else "Rascunho criado com sucesso",
            "image": image_result["status"],
        }

    def sync_wordpress_status(self) -> Dict[str, int | str]:
        pautas = excel_editorial_service.list_pautas()
        checked_count = 0
        updated_count = 0

        for pauta in pautas:
            if not pauta.url_wordpress:
                continue

            checked_count += 1
            post = wordpress_client.get_post_by_url(pauta.url_wordpress)
            if not post:
                continue

            desired_status = self._map_wordpress_status(post.get("status", ""))
            updates: Dict[str, str] = {}

            if pauta.status != desired_status:
                updates["Status"] = desired_status
            if post.get("link") and pauta.url_wordpress != post.get("link"):
                updates["URL WordPress"] = post["link"]
            if desired_status == "Publicado" and not pauta.data_publicacao:
                updates["Data publicacao"] = datetime.now().strftime("%Y-%m-%d")

            if updates:
                excel_editorial_service.update_row(pauta.id, updates)
                updated_count += 1

        return {
            "checked_count": checked_count,
            "updated_count": updated_count,
            "message": f"Sincronizacao concluida: {updated_count} pauta(s) atualizada(s) em {checked_count} verificacao(oes).",
        }


editorial_publish_service = EditorialPublishService()
