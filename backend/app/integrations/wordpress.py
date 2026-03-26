import httpx
import base64
import os
from typing import List, Dict, Any, Optional
from app.core.config import settings

class WordPressClient:
    def __init__(self):
        self.base_url = settings.WORDPRESS_URL.rstrip("/")
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.username = settings.WORDPRESS_USERNAME
        self.password = settings.WORDPRESS_APPLICATION_PASSWORD
        self.headers = self._get_auth_headers()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Gera o cabeçalho de Autenticação Básica"""
        if not self.username or not self.password:
            return {}
        # Concatenar user:pass e codificar em base64
        auth_string = f"{self.username}:{self.password}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
        return {
            "Authorization": f"Basic {auth_base64}"
        }

    def test_connection(self) -> bool:
        """Testa a conexão com o WordPress buscando o usuário logado"""
        try:
            with httpx.Client(headers=self.headers) as client:
                response = client.get(f"{self.api_url}/users/me")
                return response.status_code == 200
        except Exception as e:
            # Log de erro seria ideal aqui
            return False

    def get_categories(self) -> List[Dict[str, Any]]:
        """Lista todas as categorias"""
        with httpx.Client(headers=self.headers) as client:
            response = client.get(f"{self.api_url}/categories", params={"per_page": 100})
            if response.status_code != 200:
                raise Exception(f"Erro ao buscar categorias: {response.text}")
            return response.json()

    def create_category(self, name: str) -> int:
        """Cria uma nova categoria"""
        with httpx.Client(headers=self.headers) as client:
            response = client.post(f"{self.api_url}/categories", json={"name": name})
            if response.status_code not in [200, 201]:
                raise Exception(f"Erro ao criar categoria: {response.text}")
            return response.json()["id"]

    def get_or_create_category(self, name: str) -> Optional[int]:
        """Busca categoria por nome ou cria se não existir"""
        if not name: return None
        try:
            categories = self.get_categories()
            for cat in categories:
                if cat["name"].lower() == name.lower():
                    return cat["id"]
            return self.create_category(name)
        except Exception as e:
            print(f"Erro na gestão de categoria '{name}': {str(e)}")
            return None

    def get_tags(self) -> List[Dict[str, Any]]:
        """Lista todas as tags"""
        with httpx.Client(headers=self.headers) as client:
            response = client.get(f"{self.api_url}/tags", params={"per_page": 100})
            return response.json() if response.status_code == 200 else []

    def create_tag(self, name: str) -> Optional[int]:
        """Cria uma nova tag"""
        with httpx.Client(headers=self.headers) as client:
            response = client.post(f"{self.api_url}/tags", json={"name": name})
            return response.json()["id"] if response.status_code in [200, 201] else None

    def get_or_create_tag(self, name: str) -> Optional[int]:
        """Busca tag por nome ou cria se não existir"""
        if not name: return None
        try:
            tags = self.get_tags()
            for t in tags:
                if t["name"].lower() == name.lower():
                    return t["id"]
            return self.create_tag(name)
        except Exception as e:
            print(f"Erro na gestão de tag '{name}': {str(e)}")
            return None

    def create_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo post no WordPress"""
        # post_data deve conter: title, content, slug, excerpt, status, categories, tags, featured_media
        with httpx.Client(headers=self.headers) as client:
            response = client.post(f"{self.api_url}/posts", json=post_data)
            if response.status_code not in [200, 201]:
                raise Exception(f"Erro ao criar post: {response.text}")
            return response.json()

    def upload_media(self, file_bytes: bytes, filename: str, mime_type: str = "image/jpeg") -> int:
        """Faz upload de uma imagem para o WordPress"""
        headers = {
            **self.headers,
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": mime_type
        }
        with httpx.Client(headers=headers) as client:
            response = client.post(f"{self.api_url}/media", content=file_bytes)
            if response.status_code not in [200, 201]:
                raise Exception(f"Erro ao fazer upload de mídia: {response.text}")
            return response.json()["id"]

# Instância global
wordpress_client = WordPressClient()
