# django_reference_api

A deliberately small **Django + Django REST Framework (DRF)** reference API.

The goal is **architectural understanding**, not feature count. Read this repo
top to bottom and you will know: where a request enters, where the request body
and query parameters are read, where validation happens, where business logic
lives, where the database is touched, and where the JSON response is built.

If you already know Express/Node, treat this as "the same small REST API, but
the Django way." There is a full Express -> Django mapping table in section 5.

---

## 1. What Django is (in backend terms)

Django is a Python web framework that gives you, out of the box:

- an **ORM** (you write Python; it writes the SQL),
- a **URL router** (`urls.py` files),
- **views** (the equivalent of controllers),
- **middleware**,
- an **admin panel** (a free CRUD UI for your models),
- **migrations** (versioned, replayable database schema changes).

**Django REST Framework (DRF)** sits on top of Django and adds the pieces a
JSON API needs: **serializers** (validation + model/JSON conversion),
**`request.data` / `request.query_params`**, **`Response`**, HTTP **status
codes**, and **authentication/permission** classes.

Django ships with a lot. This repo uses a small slice of it on purpose.

---

## 2. Project vs app

This is the single most important Django idea to internalise.

| Concept | What it is | In this repo |
|---|---|---|
| **Project** | The whole site: settings, root URLs, database config. One per repo. | the `config/` package |
| **App** | A self-contained feature module: models, views, urls, tests. Many per project. | the `users/` package |

- The **project** (`config`) knows *that* apps exist and wires them together.
- The **app** (`users`) knows *how* its feature works.

There are exactly three connection points. Remember these, not syntax:

1. `config/settings.py` -> `INSTALLED_APPS = [..., "users"]` registers the app.
2. `config/urls.py` -> `path("api/users/", include("users.urls"))` mounts its URLs.
3. `users/apps.py` -> `UsersConfig` is the app's descriptor/entry point.

You could delete the `users` app and the `config` project would still boot -- it
would simply stop having that feature. That separation is the whole point.

---

## 3. Folder structure

```text
django_reference_api/          <- repo root (this folder)
├── manage.py                  <- Django's CLI entry point ("npm run" for Django)
├── requirements.txt           <- pip dependencies
├── pyproject.toml / uv.lock   <- the same dependencies, for uv users
├── .env.example               <- template for env vars (safe to commit)
├── .env                       <- YOUR values (gitignored, never committed)
├── .gitignore
├── README.md
│
├── config/                    <- THE PROJECT (configuration, no feature logic)
│   ├── settings.py            <- all configuration lives here
│   ├── urls.py                <- root router; delegates to apps
│   ├── wsgi.py / asgi.py      <- server entry points (leave alone)
│   └── __init__.py
│
└── users/                     <- THE APP (one feature: managing users)
    ├── models.py              <- database tables as Python classes
    ├── serializers.py         <- validation + model <-> JSON conversion
    ├── services.py            <- business logic (the layer that talks to the ORM)
    ├── views.py               <- HTTP handlers (read request -> return response)
    ├── urls.py                <- URL patterns for this app
    ├── middleware.py          <- cross-cutting request/response logic
    ├── admin.py               <- registers the model with Django admin
    ├── apps.py                <- the app config / entry point
    ├── tests.py               <- automated tests
    └── migrations/            <- generated, versioned schema changes
```

### The important files, one by one

- **`manage.py`** -- the command-line tool. `runserver`, `migrate`, `test`,
  `makemigrations` all go through it. It also points Python at your settings
  (`DJANGO_SETTINGS_MODULE = "config.settings"`).

- **`config/settings.py`** -- every knob: database, `INSTALLED_APPS`,
  `MIDDLEWARE`, DRF defaults, logging, and reading `.env`. If you ever wonder
  "where is X configured?", the answer is almost always here.

- **`config/urls.py`** -- the **root URLconf**. It holds no feature routes; it
  mounts each app: `path("api/users/", include("users.urls"))`.

- **`users/models.py`** -- the `User` class. One class = one database table.
  Django auto-adds an `id` primary key, and names the table `users_user`.

- **`users/serializers.py`** -- `UserSerializer`. Converts a `User` -> JSON for
  responses, and validates incoming JSON -> `validated_data` for input.

- **`users/services.py`** -- the **business-logic layer**: small functions
  (`list_users`, `get_user`, `create_user`) that talk to the ORM. Kept apart from
  views so HTTP concerns and business rules never get tangled together.

- **`users/views.py`** -- the **controllers**. Read the request, call a service,
  return a response with a status code. This is where `request.data`,
  `request.query_params`, and the URL `id` are used.

- **`users/urls.py`** -- this app's URL patterns (`""` and `"<int:id>/"`),
  relative to the `api/users/` prefix mounted in `config/urls.py`.

- **`users/middleware.py`** -- `RequestLoggingMiddleware`, which logs before and
  after each request. It shows where middleware sits in the lifecycle.

- **`users/tests.py`** -- readable tests for list/detail/create, including the
  error cases (404, 400) and a query-parameter filter.

- **`users/migrations/`** -- files generated by `makemigrations`. Each one
  describes a schema change in a way that can be replayed on any database.

---

## 4. Request lifecycle

What happens when a request arrives, and which file owns each stage:

```text
HTTP Request
    |
    v
Middleware            users/middleware.py   logs "-->"
    |
    v
URL Resolver          config/urls.py -> users/urls.py   picks the view from the path
    |
    v
View                  users/views.py        reads request.data / request.query_params / id
    |
    v
Serializer            users/serializers.py  validates input, model <-> JSON
    |
    v
Service               users/services.py     business logic
    |
    v
ORM                   users/models.py  ->  Manager (objects)  ->  SQL
    |
    v
Database              db.sqlite3 (SQLite)
    |
    v
Serializer            users/serializers.py  model instance -> JSON-ready dict
    |
    v
HTTP Response         rest_framework.response.Response  (status code + JSON)
    |
    v
Middleware            users/middleware.py   logs "<--", then returns
    |
    v
Client
```

### What each stage does

1. **Middleware** wraps everything. On the way *in* it can inspect/modify the
   request; on the way *out* it can inspect/modify the response. Ours just logs
   and times. This is the natural home for cross-cutting concerns.
2. **URL resolver** matches the path against `urlpatterns`, from
   `config/urls.py` down into `users/urls.py`, to decide *which view* to call.
   It also extracts path parameters such as `id`.
3. **View** is your controller. It reads the request, calls the right service,
   and chooses the HTTP status code. Keep it thin.
4. **Serializer** validates input (required fields, email format, uniqueness)
   and converts between model instances and JSON-ready dicts.
5. **Service** holds business logic and is the only layer besides models that
   touches the ORM.
6. **ORM / Model** turns Python method calls into SQL and back.
7. **Database** stores the rows -- here, a single SQLite file.

---

## 5. Express -> Django/DRF mapping

You already know Express, so map the new names onto the ones you know.

| Express / Node | Django / DRF | Where in this repo |
|---|---|---|
| `router` | `urls.py` (root + per app) | `config/urls.py`, `users/urls.py` |
| `app.get('/users', handler)` | `path("", view)` | `users/urls.py` |
| controller / handler | **view** | `users/views.py` |
| `req.body` | `request.data` | `users/views.py` (POST branch) |
| `req.query` | `request.query_params` | `users/views.py` (GET branch) |
| `req.params.id` | view argument from `<int:id>` | `users/urls.py` + `views.py` |
| `res.json({users})` | `Response({"users": ...})` | `users/views.py` |
| `res.status(201).json(x)` | `Response(x, status=201)` | `users/views.py` |
| model/schema (Mongoose, Sequelize) | **Django model** | `users/models.py` |
| ORM (`Model.find()`) | **Django ORM** (`User.objects.filter()`) | `users/services.py` |
| validation (Joi, Zod, express-validator) | **serializer** | `users/serializers.py` |
| service layer | **service layer** (same idea) | `users/services.py` |
| `app.use(middleware)` | `MIDDLEWARE` in settings | `config/settings.py` |
| middleware function | middleware class with `__call__` | `users/middleware.py` |
| `next()` | `self.get_response(request)` | `users/middleware.py` |
| `app.listen(3000)` | `python manage.py runserver` | `manage.py` |
| `.env` + `dotenv` | `.env` + `python-dotenv` | `config/settings.py` |
| Jest / Supertest | Django / DRF `APITestCase` | `users/tests.py` |

---

## 6. Example requests

Base URL: `http://127.0.0.1:8000`.

### GET all users

```bash
curl http://127.0.0.1:8000/api/users/
```

```json
{ "users": [ { "id": 1, "name": "Alice", "email": "alice@example.com" } ] }
```

### GET one user

```bash
curl http://127.0.0.1:8000/api/users/1/
```

```json
{ "id": 1, "name": "Alice", "email": "alice@example.com" }
```

A missing id returns HTTP 404 and `{ "detail": "User with id=9999 does not exist." }`.

### GET with query parameters

```bash
curl "http://127.0.0.1:8000/api/users/?name=Alice"
curl "http://127.0.0.1:8000/api/users/?email=alice@example.com"
```

Both are read in the GET branch of `user_list` via
`request.query_params.get(...)`, then handed to the service, which filters the
queryset. No match -> an empty `{"users": []}` list (not a 404).

### POST a user

```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

- Valid -> `201 Created` with the new user as JSON.
- Duplicate email -> `400` with `{"email": ["user with this email already exists."]}`.
- Missing/invalid data -> `400` with per-field messages.
- `PUT` / `DELETE` on this URL -> `405 Method Not Allowed` (only GET/POST declared).

Tip: open the URLs in a browser. DRF renders a **browsable HTML API** where you
can inspect responses and POST data by hand -- great for experimenting.

---

## 7. How to run

Everything below assumes you are in the repo root (the folder with `manage.py`).

### With `uv` (how this repo was set up)

```bash
uv sync                  # create .venv and install all dependencies
cp .env.example .env     # create your local env file (already done in this repo)
uv run python manage.py migrate
uv run python manage.py runserver
```

`uv run <cmd>` runs a command inside the project's virtual environment.

### With plain `pip` (no uv)

```bash
python -m venv .venv                  # 1. create a virtual environment
source .venv/bin/activate             # 2. activate it  (Windows: .venv\Scripts\activate)
pip install -r requirements.txt       # 3. install dependencies
cp .env.example .env                  # 4. create your env file
python manage.py migrate              # 5. create the database tables
python manage.py runserver            # 6. start the dev server
```

The server runs at http://127.0.0.1:8000/.

### The commands you will actually use

| Command | What it does |
|---|---|
| `python manage.py runserver` | start the dev server (auto-reloads on save) |
| `python manage.py check` | sanity-check the project configuration |
| `python manage.py makemigrations` | turn model changes into a migration file |
| `python manage.py migrate` | apply migrations to the database |
| `python manage.py test` | run the test suite |
| `python manage.py createsuperuser` | create a login for `/admin/` |
| `python manage.py shell` | an interactive Python shell with Django loaded |

---

## 8. Error handling

The status codes this API returns, and where each decision is made:

| Situation | Status | Produced by |
|---|---|---|
| Everything is fine (GET) | `200 OK` | `users/views.py` |
| A resource was created (POST) | `201 Created` | `users/views.py` |
| Invalid body / missing field / bad email / duplicate email | `400 Bad Request` | `users/serializers.py` (validation), returned by the view |
| User not found | `404 Not Found` | `users/views.py` (catches `User.DoesNotExist`) |
| Method not allowed (e.g. PUT) | `405 Method Not Allowed` | DRF, from `@api_view(["GET", "POST"])` |

Error bodies are JSON, one message per field:

```json
{ "email": ["user with this email already exists."] }
{ "name": ["This field is required."], "email": ["Enter a valid email address."] }
```

---

## 9. Authentication & permissions (concepts)

This API is intentionally **public**, but DRF gives you auth for free when you
want it. The relevant settings are in `config/settings.py`:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [SessionAuthentication, BasicAuthentication],
    "DEFAULT_PERMISSION_CLASSES": [AllowAny],  # -> IsAuthenticated to lock it down
}
```

- **Authentication** = *who are you?* (`BasicAuthentication` reads an
  `Authorization: Basic ...` header; `SessionAuthentication` uses the login
  cookie that `/admin/` uses).
- **Permissions** = *are you allowed?* (`AllowAny`, `IsAuthenticated`, ...).

To require login on one endpoint, decorate the view in `users/views.py`:

```python
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_list(request):
    ...
```

Unauthenticated callers then get `401`/`403` automatically. This is the Django
equivalent of an Express auth middleware -- except it is declarative.

---

## 10. Tests

`users/tests.py` uses DRF's `APITestCase`. Run it with:

```bash
python manage.py test          # or: uv run python manage.py test
```

The suite covers: list users, get one user, 404 for a missing user, create a
valid user, 400 for invalid input, 400 for a duplicate email, and filtering by
query parameter. Read it as executable documentation of the API's behaviour.

---

## 11. Where do I put new functionality?

The questions you will actually ask, and their answers:

| Question | Answer |
|---|---|
| Where does a GET request enter Django? | `config/urls.py` -> `users/urls.py` -> the view |
| Where does a POST request go? | the same path; the POST branch of `user_list` |
| Where do I read the request body? | `request.data`, in `users/views.py` |
| Where do I read query parameters? | `request.query_params`, in `users/views.py` |
| Where do path parameters come from? | the `<int:id>` pattern in `users/urls.py`; the view gets `id` |
| Where does validation happen? | `users/serializers.py` |
| Where does business logic live? | `users/services.py` |
| Where is the database touched? | `users/services.py` (via `users/models.py` + the ORM) |
| Where do I define a table/column? | `users/models.py`, then `makemigrations` + `migrate` |
| Where do I return JSON? | `Response(...)` in `users/views.py` |
| Where does middleware run? | `users/middleware.py`, registered in `config/settings.py` |
| How does the app connect to the project? | `INSTALLED_APPS` + `include(...)` in `config/urls.py` |
| Where is configuration? | `config/settings.py` (plus values from `.env`) |

### Adding a brand-new feature (say, `posts`)

```bash
python manage.py startapp posts                       # 1. create the app
# 2. add "posts" to INSTALLED_APPS in config/settings.py
# 3. add path("api/posts/", include("posts.urls")) in config/urls.py
# 4. write models.py, serializers.py, services.py, views.py, urls.py, tests.py
python manage.py makemigrations posts && python manage.py migrate
```

That is the whole loop. The shape is always the same as `users/`.

---

## 12. Recommended reading order

Do not start at `settings.py`; start where a request starts.

```text
config/urls.py         (1) where a request enters
    |
users/urls.py          (2) which view handles which path
    |
users/views.py         (3) read request.data / query_params / id, return Response
    |
users/serializers.py   (4) what is valid; model <-> JSON
    |
users/services.py      (5) business logic
    |
users/models.py        (6) the table + the ORM
    |
users/middleware.py    (7) the code that wraps all of the above
    |
config/settings.py     (8) how everything is wired together
    |
users/tests.py         (9) the behaviour, in executable form
```

---

## 13. Keeping it small on purpose

This repo deliberately avoids the things that make Django projects hard to read
as a beginner:

- **no** generic viewsets/routers (they hide which URL maps to which method),
- **no** repository/domain layers, factories, or abstract base classes,
- **no** signals, custom managers, or "magic" helper utilities,
- **no** Postgres/Redis/Celery/Docker -- just SQLite, so it runs instantly.

Simple and obvious beats "enterprise" when the goal is understanding. Once the
shape above feels natural, `ModelViewSet` and friends become easy to adopt --
and you will understand exactly what they are doing for you.





