# Food Lab Backend

A multi-vendor food ordering backend built with Django REST Framework, Django Channels (WebSocket), and a mounted FastAPI service under the same ASGI app.

## Core Features
- Role-based authentication (Customer/Seller) with JWT
- Email/mobile OTP-based password reset flow
- Google and Apple social login
- Seller shop management (profile, images, documents, map/nearby search)
- Product CRUD, search, reviews, seller reply/report flow
- Cart management and checkout
- Order lifecycle for customer and seller
- Stripe payment integration (Checkout + Webhook)
- Real-time chat (customer <-> seller) via WebSocket
- In-app notifications + Firebase push notifications (FCM)
- Dashboard endpoints for summary, revenue, and customer charts
- Additional FastAPI routes mounted at `/fast`

## Tech Stack
- Python, Django, Django REST Framework
- Django Channels, ASGI, WebSocket
- FastAPI, Starlette, Uvicorn
- SimpleJWT, dj-rest-auth, django-allauth
- Stripe SDK
- Firebase Admin SDK
- Geopy (Nominatim)
- SQLite (default in this repo)

## Project Structure
```text
project/                  # Django project settings/urls/asgi
apps/
  authentication/         # Auth, profiles, OTP, social login
  seller/                 # Shop + geo/nearby logic
  seller_profile/         # Seller profile related APIs
  customer_profile/       # Address/profile endpoints
  product/                # Product + review management
  cart/                   # Cart + checkout flow
  order/                  # Orders + Stripe webhook + seller updates
  chatting/               # Chat APIs + websocket consumer
  notification/           # Notifications + FCM token flow
  dashboard/              # Summary/revenue/customer analytics
  crave/                  # Short video module (upload/like/report)
  fastapi_app/            # Mounted FastAPI routes
middleware/
```

## Quick Start
### 1. Clone and install
```bash
git clone <your-repo-url>
cd food-lab
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment
Create a `.env` (or system env vars) and set at least:

```env
DJANGO_SETTINGS_MODULE=project.settings
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FIREBASE_CRED_PATH=food-lab-firebase.json
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### 3. Migrate and run
```bash
python manage.py migrate
python manage.py runserver
```

Base URL (default): `http://127.0.0.1:8000/`

## API Routing Overview
- Django APIs: `/api/v1/...`
- Auth (dj-rest-auth): `/auth/...`
- FastAPI mount: `/fast/...`
- Admin: `/admin/`

## Common Endpoint Groups
- Authentication: signup/login/logout/profile/token refresh/password reset/OTP
- Product: create/list/detail/search/review/reply/report
- Cart: list/add/increase/decrease/delete/checkout
- Order: customer create/list/feedback, seller list/update/summary, Stripe webhook
- Seller Shop: shop CRUD, images, documents, map, nearby, search
- Chat: chat room create/list, message list/create, websocket room stream
- Notification: list, mark read, device token registration
- Dashboard: summary/revenue/customers

## WebSocket Chat
- Route pattern: `ws://<host>/ws/chat/<room_id>/?token=<jwt_access_token>`
- Auth is JWT-based via custom Channels middleware.

## FastAPI Integration
`project/asgi.py` mounts FastAPI and Django together:
- `/fast/*` -> FastAPI app
- `/*` -> Django ASGI app

## Notes
- This repository currently uses SQLite (`db.sqlite3`) for local development.
- `CHANNEL_LAYERS` is configured with in-memory backend; use Redis for production.
- Keep all secret keys/tokens in environment variables for production.

## Test
```bash
python manage.py test
```

## License
This project currently has no explicit license file in the repository.
