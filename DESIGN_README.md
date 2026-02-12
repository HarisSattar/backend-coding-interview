# Photo Management API

A RESTful API for managing photos and photographers, built with Django and Django REST Framework.

## Architecture Decisions

### Tech Stack
- **Django + DRF** - Chose Django REST Framework because it provides serialization, authentication, permissions, pagination, and filtering out of the box. This makes 
setup fast and simple.
- **PostgreSQL** - Relational data with clear relationships (e.g. users own photos, photos belong to photographers). PostgreSQL handles UUID primary keys natively and scales well.
- **JWT Authentication** - Stateless auth using `djangorestframework-simplejwt`. No server-side session storage needed, works well for API consumers.
- **Docker Compose** - Reproducible dev environment with PostgreSQL, no local database setup required.

### Data Model
- **User** - Custom model with email-based authentication. UUIDs as primary keys to avoid exposing sequential IDs.
- **Photographer** - Separate model for photo creators. One photographer can have many photos. Created via CSV import or inline when creating a photo.
- **Photo** - Core resource with metadata from Pexels provided in the CSV file. Each photo belongs to one photographer and optionally to one user (owner).

### API Design Trade-offs
- **Flat resource endpoints over nested** - Photos are managed by `/api/v1/photos/` rather than nested under `/users/{id}/photos/`. Ownership is enforced through permissions, not URL structure. This keeps the API surface small and avoids duplicating logic.
- **Photographers are read-only** - Listed by `/api/v1/photographers/` but not directly editable. They're created either through CSV import or inline when creating a photo. Corrections can be made by `new_photographer_name`/`new_photographer_url` fields on photo update, or by admins through Django's admin panel.
- **Photographer immutable by UUID on update** - Users can't reassign a photo to a different photographer by UUID. They can correct photographer details using the `new_photographer_name`/`new_photographer_url` fields, which uses `get_or_create` to avoid duplicates.
- **Filtering by query params** - Instead of building nested endpoints for every relationship (e.g., `/photographers/{id}/photos/`), photos are filterable by `?photographer=<uuid>`. This scales better when combining multiple filters.

## Features Implemented

### Authentication & Authorization
- Email-based user registration with password hashing
- JWT token authentication (login + refresh)
- Owner-based permissions: only photo owners or admins can modify/delete
- Unauthenticated users can read photos and photographers

### Photo Management (CRUD)
- Full REST endpoints: list, create, retrieve, update, delete
- Create with existing photographer (UUID) or new photographer (name + URL)
- Owner automatically set to authenticated user on creation

### Filtering, Search & Ordering
- **Filter** photos by: `photographer`, `avg_color`, `owner`
- **Search** photos by: `alt` text, photographer name
- **Search** photographers by: `name`
- **Order** photos by: `created_at`, `width`, `height`
- **Order** photographers by: `name`, `created_at`

### Pagination
- Page-based pagination (20 items per page) on all list endpoints
- Response includes `count`, `next`, `previous`, and `results`

### Data Import
- Management command to ingest `photos.csv` into the database
- Creates photographer records automatically from CSV data

### Rate Limiting
- **DRF Throttling**: Rate limiting is enforced using Django REST Framework's `AnonRateThrottle` and `UserRateThrottle` settings. Anonymous and authenticated users are limited to a configurable number of requests per minute. This helps prevent abuse and ensures fair API usage.

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/users/register/` | Register a new user | No |
| POST | `/api/v1/auth/login/` | Get JWT access + refresh tokens | No |
| POST | `/api/v1/auth/refresh/` | Refresh an access token | No |

### Photos
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/photos/` | List photos (paginated, filterable) | No |
| POST | `/api/v1/photos/` | Create a photo | Yes |
| GET | `/api/v1/photos/{id}/` | Get a single photo | No |
| PATCH | `/api/v1/photos/{id}/` | Update a photo | Yes (owner/admin) |
| DELETE | `/api/v1/photos/{id}/` | Delete a photo | Yes (owner/admin) |

**Query parameters for GET `/api/v1/photos/`:**
- `?photographer=<uuid>` - filter by photographer
- `?avg_color=<hex>` - filter by average color
- `?owner=<uuid>` - filter by owner
- `?search=<text>` - search alt text and photographer name
- `?ordering=created_at|-created_at|width|-width|height|-height`
- `?page=<n>` - pagination

### Photographers
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/photographers/` | List photographers (paginated) | No |

**Query parameters:**
- `?search=<text>` - search by name
- `?ordering=name|-name|created_at|-created_at`
- `?page=<n>` - pagination

### API Docs
| Method | Endpoint |
|--------|----------|
| OpenApi | `/api/schema/` |
| Swagger | `/api/doc/` |
| ReDoc | `/api/redoc/` |

## Setup & Running

### Prerequisites
- Docker and Docker Compose

### Start the application
```bash
docker compose up --build
```

### Run migrations and import data
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py import_photos
```

### Create a superuser (optional, for admin panel)
```bash
docker compose exec web python manage.py createsuperuser
```

The API is available at `http://localhost:8000/api/v1/`.
The admin panel is at `http://localhost:8000/admin/`.

### Run tests
```bash
docker compose exec web python manage.py test
```

### Postman Collection
Import `clever_assignment.postman_collection.json` into Postman to test all endpoints. The collection includes auto-saved variables for tokens and IDs.

## Testing Strategy

Tests are organized by app with focused test classes:

- **Users** (11 tests) - Registration validation (success, duplicate, missing fields, email normalization, password hashing), JWT login/refresh flows
- **Photos** (25 tests) - CRUD operations, permission enforcement (owner/non-owner/admin/unauthenticated), photographer immutability, inline photographer creation and deduplication, filtering, search, ordering, pagination
- **Photographers** (6 tests) - Listing, search, ordering, pagination
- **Core** (2 test) - Management command for importing photos from CSV (`import_photos`). Test for health check

Total: **43 tests** covering the core API behavior, permissions, and edge cases.

## What I Would Add With More Time

- **Logging** Structured logging, logging for request/response and error tracking
- **CI/CD pipeline** with automated test runs
- **Additional Feature: Photo bulk actions** bulk actions for easier management of large datasets
- **Advanced filtering and faceted search** by date range, color similarity, or tag
- **Performance optimizations** query optimization, caching, async import

## Assumptions

- **Photographer management**: Photographers are primarily sourced from the initial CSV import and can also be created inline when a new photo is added. There is no dedicated endpoint for creating, updating, or deleting photographers directly through the API. This simplifies the model and reflects the assumption that photographers are not a frequently changing resource in this context.
- **Photo metadata handling**: All photo metadata is stored exactly as provided by the source (CSV file).
- **CSV import scale**: The `photos.csv` dataset is assumed to be small enough to be imported in a single run of the management command, without the need for batching, chunking, or background processing. For much larger datasets, additional logic would be required to handle memory and transaction limits.
- **UUID primary keys**: All models use UUIDs as primary keys to avoid exposing sequential integer IDs, which can be a security risk and make enumeration attacks easier. This also ensures global uniqueness across distributed systems.
- **JWT token lifetime**: JWT access tokens are configured with a 1-day lifetime for development convenience, allowing for easier testing and longer sessions. In a production environment, this value should be much shorter (e.g., 15 minutes) to reduce the risk of token compromise.
- **Testing environment**: The test suite assumes a clean database state and may create or delete data as needed. Tests are not designed to run against a production database.
