# 📘 Inventory Management System (IMS)

This Django-based Inventory Management System (IMS) is a scalable, multi-tenant backend application built to manage inventory operations across  multiple tenants. It supports fine-grained access control, optimized API routing, and production-ready deployment with Docker and Nginx.

## 🧰 Prerequisites

- 🐍 Python 3.12+

- 🐳 Docker 28.2+

- 🧱 Docker Compose v2.24+

- 🌐 Git 2.25+

- 🗃️ SQLite 3.45+

- ⚡ Memcached 1.6+

## 🚀 Installation and Setup

After installing the prerequisites, follow the steps below to get your project running using Docker:

```bash
# 1️⃣ Start Docker containers (build & run in detached mode)
sudo docker-compose up --build -d

# 2️⃣ Get a bash shell inside the running container
docker exec -it <container_name_or_id> bash

# 3️⃣ Run database migrations
python manage.py migrate

# 4️⃣ Load initial data using a custom Django command
python manage.py load_data
```

## 🔑 Key Features

- 🏢 **Tenant-wise Database Configuration**:
Seamless support for both **shared** and **isolated** databases. Each tenant can configure their own database strategy.
  - Tenants can operate on:
    - A **shared RDBMS database**, or
    - **Isolated databases** per Tenant
    - 🔌 **Database Backend is Pluggable**: Easily extend support for **NoSQL databases** (e.g. MongoDB) or other RDBMS by abstracting DB access layer.

----

- 🔐 **Tenant-wise Configurable Authentication and Authorization**
  Each tenant can independently choose the authentication strategy:
  - **JWT-based authentication**
  - **Token-based authentication**
  - 🔌 **Pluggable Design**: Easily extendable to integrate other mechanisms like **SAML SSO**, **OAuth2**, or **LDAP** as needed.
  - Fine-grained access control where each API endpoint can be enabled or restricted per role, allowing admins to dynamically assign permissions to roles.

----

- ⚡ **Tenant-aware Caching**: Support for in-memory and Memcached caching with tenant-specific keys for isolated performance. A unified caching interface abstracts the underlying cache system, with current support for:
  - **In-memory cache**
  - **Memcached**
  - 🔌 Additional backends (like Redis) can be plugged in easily by extending the interface

----

- 🌐 **Subdomain-Based Tenant Identification**
  Every request is dynamically routed to the correct tenant using a custom middleware:
  - Extracts the **subdomain** from the incoming request
  - Fetches **tenant metadata** from cache or DB
  - Binds tenant info to a **thread-local context**
  - Automatically rejects invalid or unknown subdomains with a `400 Bad Request`

  ✅ Smart behavior:
  - Excludes specific routes (like health checks or login) using path-exclusion logic
  - Tenant-aware state is auto-cleared after each request for thread safety

  🔄 *Cached Tenant Resolution
  Uses caching (like Memcached) to speed up tenant lookup on repeated requests.*

----

- 🧱 **Generic CRUD BaseView**
  Build the custom **generic CRUD view class** that handles all standard Create, Read, Update, and Delete operations with minimal boilerplate.
  Just inherit `BaseView` and plug in:
  - Your `serializer_class`
  - Your `db-access layer`

  ✅ Supports:
  - `search_fields` for full-text search
  - `filter_fields` for field-based filtering
  - `is_pagination = True` to enable built-in paginated responses

  🔧 You can override any method for full customization, making it a powerful foundation for rapid API development.

----

- 🚨 **Centralized Exception Middleware**
  All unhandled exceptions in the API pipeline are caught and transformed into structured JSON responses.

  ✅ Features:
  - Logs full traceback details using a centralized logger
  - Converts DRF `ValidationError` into frontend-friendly JSON with detailed formatting
  - Handles custom application exceptions like:
    - `NoDataFoundError`
    - `BadRequestError`
    - `PermissionDenied`
    - `UnauthorizedException`
    - `WrongCredentialsException`
  - Returns consistent error codes and messages using the shared `utils.messages` and `utils.exceptions.codes`

  🛡 Ensures even unexpected errors return a proper **500 Internal Server Error** response with a structured payload — no raw stack traces exposed to the client.

----

- ⏱ **Performance & Version Middleware**
  Automatically adds useful diagnostic metadata to every API response.

  📦 Headers Added:
  - `Version`: Application version (from `get_version_str()`)
  - `Req-Performance-Time`: Time taken to process the request
    Example: `0:00:00.023456 [HH:MM:SS:MS] | 23.456[MS]`

  🔧 Useful for:
  - Debugging latency issues
  - CI/CD version traceability
  - Frontend debugging without needing separate instrumentation

----

- 🐞 **Logging**: Custom `log_msg` utility that logs with function context, reference data, and emoji-level markers in local Linux environments.

  - 🛑 **Print Statement Control**
  Disable all `print()` statements project-wide (excluding virtual environments) using a single toggle in your config. To force to use the logger:
  - `DISABLE_PRINT = true` → Suppresses all print calls
  - `DISABLE_PRINT = false` → Allows print statements (default for development)

  - 📜 **Audit Logs**: Capture every API request post-authentication, including method, path, user, and more.

----

- 📄 **Environment Configuration via JSON**
  Custom environment variables are loaded from a centralized `env.json` file using a helper function (`load_env()`), enabling:
  - Clean separation of config from code
  - Easier environment overrides for local/dev/prod/Docker

  These features offer maximum flexibility for multitenant deployments while maintaining centralized control.

----

- 🌍 **CORS Support**:
  Fully configured **Cross-Origin Resource Sharing** for seamless frontend-backend integration.
  ✅ By default, CORS is open to all origins (`CORS_ALLOW_ALL_ORIGINS = True`) for development convenience.
  🔧 This can be restricted by setting `CORS_ALLOWED_ORIGINS` in environment-specific configuration for production.

----

- 📤 **Unified Response Format**: All API responses follow a consistent structure using a centralized `generate_response` utility.

----

- 🌐 **Tenant-aware Swagger/OpenAPI Docs**: Auto-generated API docs that dynamically reflect only the endpoints accessible to the current tenant.

----

- 🐳 **Docker**: Full Docker setup with `Dockerfile`, `docker-compose.yml`, and volume mapping for multi-DB support (e.g. SQLite or pluggable RDBMS).

----

- 🧭 **Nginx as Reverse Proxy**: Production-ready Nginx configuration routing traffic to Gunicorn securely and efficiently.

----

### 🔍 Test Coverage Status

📊 **Test Coverage: 98%**

- ✅ All modules are covered with unit tests
- ✅ DRF serializers, views, middleware, and exceptions tested
- ✅ Negative and edge cases are validated
- Check the coverage report by clicking on [📊 Report](files/coverage/coverage_report.pdf)

## 🛠️ Versioning Management Command

Manage application versioning using a dedicated Django management command.

```bash
python manage.py ver <version_update_type>

# 🔼 Major update (new modules)
python manage.py ver MJ

# ➕ Minor update (new functionality)
python manage.py ver MN

# 🐞 Bug fix update
python manage.py ver BF

# 📋 Show current version
python manage.py ver CV
```

| Type      | Code | Description                     |
| --------- | ---- | ------------------------------- |
| 🔼 Major   | `MJ` | Breaking changes or new modules |
| ➕ Minor   | `MN` | New features or enhancements    |
| 🐞 Bug Fix | `BF` | Bug fixes and patches           |
| 📋 Current | `CV` | View the current version        |

## 📚 API Modules Summary

| Module          | Endpoint Prefix         | Description                                |
| --------------- | ----------------------- | ------------------------------------------ |
| 👤 User Mgmt     | `/api/user/`            | Manage users, profiles, and admin creation |
| 🔐 Auth          | `/api/auth/`            | Login and logout for users and admins      |
| 🛡 Permissions   | `/api/permission/`      | List and manage available permissions      |
| 🧩 Roles         | `/api/role-permission/` | Assign/unassign permissions to roles       |
| 🏷 Category      | `/api/category/`        | CRUD operations on categories              |
| 📦 Products      | `/api/product/`         | Manage products under categories           |
| 📥 Stock Mgmt    | `/api/stock/`           | Handle product IN/OUT transactions         |
| 📊 Reports       | `/api/report/`          | Generate stock summary and reporting APIs  |
| 📬 Notifications | `/api/notification/`    | List tenant notifications                  |
| 🧾 Audit Logs    | `/api/audit-logs/`      | Track user actions and API requests        |
| 🏢 Tenant Mgmt   | `/api/tenant/`          | Manage tenant lifecycle and configurations |
| 🧪 Health Check  | `/api/health`           | Check service health status                |

## 📚 API Documentation

The system includes complete and dynamic API documentation:

- 📖 **Swagger UI** – Available at [`/api/docs`](http://localhost/api/docs). It dynamically adapts based on tenant access and visibility.
- 📘 **ReDoc** – Available at [`/api/redoc`](http://localhost/api/redoc) for a cleaner, read-only reference experience.
- 📬 **OpenAPI Schema** – Can be fetched at [`/api/schema`](http://localhost/api/schema) for integration with external tools.

- You can download the swagger schema.
  - [Super Admin View](files/swagger/super_admin_schema.yaml)
  - [Tenant View](files/swagger/tenant_schema.yaml)

- OR

- Checkout the swagger view in pdf
  - [Super Admin View](files/swagger/super_admin_swagger_view.pdf)
  - [Tenant View](files/swagger/tenant_swagger_view.pdf)

### 🔁 Postman Collection

- ✅ A Postman collection is available with:
  - Auth token automatically saved to environment after login (`post-request` script included)
  - Subdomain captured and set in environment variables
- 📦 Import the collection and environment files from the `postman/` directory.
  - [Environment Config](files/postman/IMS.postman_environment.json)
  - [Postman Collection](files/postman/IMS.postman_collection.json)

## 👨‍💻 Author

- 🧑‍💻 Deepak sahani
