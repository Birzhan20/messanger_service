1) Переместите dump2.sql в корневую директорию
2) Создайте env файл с апи ключом
3) Примените алембик миграций
4) Запустите докер

Настройки Pocketbase
1) Создайте новую коллекцию по ссылке "http://localhost:8090/_/#/collections?collection=_pb_users_auth_&filter=&sort=-%40rowid"
    name = "documents"
    create new fiels --> "field"

2) В настройках добавьте данные "http://localhost:8090/_/#/settings"
    и кликните "Force path-style addressing"

.env for pocketbase
```
POCKETBASE_ADMIN_EMAIL=admin@mytrade.kz
POCKETBASE_ADMIN_PASSWORD=""
POCKETBASE_URL=http://pocketbase:8090
POCKETBASE_COLLECTION=documents
POCKETBASE_FIELD_NAME=document

S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=""
S3_SECRET_KEY=""
S3_BUCKET=mytrade-files
```

.env example
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=messenger_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/messenger_db
DATABASE_URL_LOCAL=postgresql+asyncpg://postgres:postgres@localhost:5432/messenger_db


GROK_API_URL=https://api.x.ai/v1/chat/completions
GROK_API_KEY="Your GROK API key"
SUPPORT_PROMPT_PATH=./prompts.docx
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```
1️⃣ GET /support/chat/{user_id}

Возвращает последние сообщения пользователя (до 20), чтобы показать историю чата.

2️⃣ POST /support/chat

Принимает сообщение от пользователя, сохраняет его и получает ответ от AI (Grok), который тоже сохраняется.

3️⃣ GET /support/prompt

Возвращает текущий системный промпт для Grok.

4️⃣ PUT /support/prompt

Обновляет текст системного промпта.

5️⃣ POST /support/prompt/upload

Загружает новый промпт из файла и сохраняет его для использования AI.