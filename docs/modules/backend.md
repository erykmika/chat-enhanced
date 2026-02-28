# Backend modules

- `backend/webapp`: Flask API application. Wires routes, config, and database access for auth and chat endpoints.
- `backend/webapp/auth`: Authentication domain, models, and HTTP API. Handles users, confirmation, and JWT issuance.
- `backend/webapp/chat`: Chat HTTP API. Lists active users and validates requests via JWT.
- `backend/webapp/database`: SQLAlchemy setup and session management.
- `backend/common`: Shared helpers, including JWT utilities.
- `backend/ws_server`: WebSocket server for realtime chat connections (separate from the Flask API).

