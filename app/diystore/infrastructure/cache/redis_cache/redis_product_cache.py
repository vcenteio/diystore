from typing import Optional

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

    def _generate_product_key(self, product_id: str):
        return f"product:{product_id}"

    def _generate_products_key(self, args: dict):
        return ":".join(v for v in ("products", *args.values()))

    def get_one(self, product_id: str) -> Optional[str]:
        key = self._generate_product_key(product_id)
        return self._conn.get(key)

    def get_many(self, args: dict) -> Optional[str]:
        key = self._generate_products_key(args)
        return self._conn.get(key)

    def set_one(self, product_id: str, representation: str):
        key = self._generate_product_key(product_id)
        return self._conn.set(key, representation, ex=self._ttl)

    def set_many(self, args: dict, representation: str):
        key = self._generate_products_key(args)
        return self._conn.set(key, representation, ex=self._ttl)

    def del_one(self, product_id: str):
        key = self._generate_product_key(product_id)
        self._conn.delete(key)

    def del_many(self, args: dict):
        key = self._generate_products_key(args)
        self._conn.delete(key)
