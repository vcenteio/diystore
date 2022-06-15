from uuid import UUID
from typing import Union


def validate_id(_id: Union[UUID, bytes, int, str], key: str):
    if _id is None:
        raise TypeError(f"{key} is a non-nullable field")
    if not isinstance(_id, (UUID, bytes, int, str)):
        raise TypeError("id must be an UUID, bytes, int or str object")
    if isinstance(_id, UUID):
        return _id.bytes
    if isinstance(_id, bytes):
        return UUID(bytes=_id).bytes
    if isinstance(_id, int):
        return UUID(int=_id).bytes
    return UUID(_id).bytes
