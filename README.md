# Real-time chat web app

### Development setup

```
uv venv
uv pip install pre-commit
pre-commit install
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running alembic

```
alembic check
alembic upgrade head
```

#### Creating a new migration
```
alembic revision --autogenerate -m "<msg>"
```