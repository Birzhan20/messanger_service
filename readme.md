.env example
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=messenger_db
POSTGRES_HOST=posgres
POSTGRES_PORT=5432

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/messenger_db

GROK_API_URL=https://api.x.ai/v1/chat/completions
GROK_API_KEY="Your api key"
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