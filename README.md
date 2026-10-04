# Quiz Conquest

Викторина с Django REST Framework backend и React + Vite frontend.

## Структура

```text
Quiz/
├── backend/        # Django проект (config) и приложения accounts, questions, games
└── frontend/       # React + Vite клиент
```

## Backend

### Инсталиране

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows PowerShell: `py -m venv .venv` и `.\.venv\Scripts\Activate.ps1`.

### Миграции

```bash
python manage.py migrate
```

### Начална банка с въпроси

```bash
python manage.py loaddata questions/question_bank.json
```

Зарежда 6 категории, 12 въпроса с избираем отговор, 48 отговора и 12 въпроса
с числов отговор.

### Администратор

```bash
python manage.py createsuperuser
```

### Стартиране

```bash
python manage.py runserver
```

Backend: `http://127.0.0.1:8000/`, Django admin: `http://127.0.0.1:8000/admin/`.

### Тестове

```bash
python manage.py test
```

Само едно приложение: `python manage.py test accounts`, `python manage.py test questions`,
`python manage.py test games`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173/`. Vite проксира `/api` към
`http://127.0.0.1:8000`, за да останат session cookie-то и CSRF token-ът
same-origin по време на разработка. Двата сървъра се стартират паралелно.

## API

| Method | Endpoint | Достъп |
|---|---|---|
| `GET` | `/api/auth/csrf/` | Public |
| `POST` | `/api/auth/register/` | Public |
| `POST` | `/api/auth/login/` | Public |
| `POST` | `/api/auth/logout/` | Authenticated |
| `GET` | `/api/auth/me/` | Authenticated |
| `PATCH` | `/api/auth/me/` | Authenticated |

Authentication: Django session authentication. Unsafe заявките изискват
`X-CSRFToken` header. Грешките се връщат в единен формат:

```json
{ "errors": { "email": ["User with this email already exists."] } }
```

## Milestones

| Tag | Съдържание |
|---|---|
| `m0-setup` | Начална структура, Django + DRF, React + Vite |
| `m1-auth` | Custom user, профил, регистрация, вход, изход, `/me` |
| `m2-question-bank` | Категории, въпроси, answer options, fixture |
| `m3-games` | Игри, участници, рундове, отговори |
