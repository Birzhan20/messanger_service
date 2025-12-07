# import httpx
# from core.config import settings

# class PocketBaseClient:
#     def __init__(self):
#         self.token = None

#     async def auth_admin(self):
#         async with httpx.AsyncClient() as client:
#             r = await client.post(
#                 f"{settings.POCKETBASE_URL.rstrip('/')}/api/collections/_superusers/auth-with-password",
#                 json={"identity": settings.POCKETBASE_ADMIN_EMAIL, "password": settings.POCKETBASE_ADMIN_PASSWORD}
#             )
#             r.raise_for_status()
#             self.token = r.json()["token"]

#     async def upload_file(self, file_bytes: bytes, filename: str):
#         if not self.token:
#             await self.auth_admin()

#         files = {"field": (filename, file_bytes)}
#         headers = {"Authorization": f"Bearer {self.token}"}

#         async with httpx.AsyncClient() as client:
#             r = await client.post(
#                 f"{settings.POCKETBASE_URL}/api/collections/{settings.POCKETBASE_COLLECTION}/records",
#                 headers=headers,
#                 files=files
#             )
#             r.raise_for_status()
#             data = r.json()
#             print("POCKETBASE RESPONSE:", data)

#             file_field = data.get("field")
#             if isinstance(file_field, list):
#                 file_url_path = file_field[0]["url"]
#             elif isinstance(file_field, str):
#                 file_url_path = file_field
#             else:
#                 raise ValueError("Неизвестный формат поля файла в PocketBase")

#             return f"{settings.POCKETBASE_URL}{file_url_path}"





import httpx
from core.config import settings

class PocketBaseClient:
    def __init__(self):
        self.token = None

    async def auth_admin(self):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.POCKETBASE_URL.rstrip('/')}/api/collections/_superusers/auth-with-password",
                json={"identity": settings.POCKETBASE_ADMIN_EMAIL, "password": settings.POCKETBASE_ADMIN_PASSWORD}
            )
            r.raise_for_status()
            self.token = r.json()["token"]

    async def upload_file(self, file_bytes: bytes, filename: str):
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
