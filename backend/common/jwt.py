import jwt


class JwtService:
    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key

    def encode(self, payload: dict) -> str:
        return jwt.encode(payload, self._secret_key, algorithm="HS256")

    def decode(self, token: str) -> dict:
        return jwt.decode(token, self._secret_key, algorithms=["HS256"])
