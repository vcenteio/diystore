from typing import Optional
from hashlib import sha1

from redis import Redis

from ..interfaces import Cache


class RedisRepresentationCache(Cache):
    def __init__(
        self,
        host: str,
        port: int,
        db: int = 0,
        password: str = None,
        ssl: bool = True,
        ttl: int = 360,
    ):
        self._conn = Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            ssl=ssl,
            ssl_cert_reqs=None,
        )
        self._ttl = ttl

    def _generate_key(self, **kwargs: dict):
        return ":".join(v for v in kwargs.values())

    def get(self, **kwargs) -> Optional[str]:
        key = self._generate_key(**kwargs)
        return self._conn.get(key)

    def set(self, representation: str, **kwargs):
        key = self._generate_key(**kwargs)
        return self._conn.set(key, representation, ex=self._ttl)

    def delete(self, **kwargs):
        key = self._generate_key(**kwargs)
        self._conn.delete(key)
