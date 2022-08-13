from typing import Optional
from hashlib import sha1

from redis import Redis

from ..interfaces import ProductCache


class RedisProductRepresentationCache(ProductCache):
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
            host=host, port=port, db=db, password=password, decode_responses=True, ssl=ssl, ssl_cert_reqs=None
        )
        self._ttl = ttl

    def _generate_document_key(self, _id: str):
        return sha1(_id.encode()).hexdigest()

    def _generate_collection_key(self, args: dict):
        return sha1(":".join(v for v in args.values()).encode()).hexdigest()

    def get_one(self, _id: str) -> Optional[str]:
        key = self._generate_document_key(_id)
        return self._conn.get(key)

    def get_many(self, **args: dict) -> Optional[str]:
        key = self._generate_collection_key(args)
        return self._conn.get(key)

    def set_one(self, *, representation: str, _id: str):
        key = self._generate_document_key(_id)
        return self._conn.set(key, representation, ex=self._ttl)

    def set_many(self, *, representation: str, **args: dict):
        key = self._generate_collection_key(args)
        return self._conn.set(key, representation, ex=self._ttl)

    def del_one(self, _id: str):
        key = self._generate_document_key(_id)
        self._conn.delete(key)

    def del_many(self, **args: dict):
        key = self._generate_collection_key(args)
        self._conn.delete(key)
