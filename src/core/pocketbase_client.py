import httpx
from core.config import settings


class PocketBaseClient:
    """Клиент для загрузки файлов в PocketBase."""

    def __init__(self):
        self.token = None

    async def auth_admin(self):
        """Аутентификация администратора в PocketBase."""
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.POCKETBASE_URL.rstrip('/')}/api/collections/_superusers/auth-with-password",
                json={"identity": settings.POCKETBASE_ADMIN_EMAIL, "password": settings.POCKETBASE_ADMIN_PASSWORD}
            )
            r.raise_for_status()
            self.token = r.json()["token"]

    async def upload_file(self, file_bytes: bytes, filename: str):
        """Загружает файл в PocketBase и возвращает URL."""

        if not self.token:
            await self.auth_admin()

        files = {"field": (filename, file_bytes)}
        headers = {"Authorization": f"Bearer {self.token}"}

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.POCKETBASE_URL}/api/collections/{settings.POCKETBASE_COLLECTION}/records",
                headers=headers,
                files=files
            )
            r.raise_for_status()
            data = r.json()
            print("POCKETBASE RESPONSE:", data)
            return f"{settings.POCKETBASE_URL.rstrip('/')}/api/files/{settings.POCKETBASE_COLLECTION}/{data['id']}/{data['field']}"
