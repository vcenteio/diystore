from uuid import UUID
from typing import Union


def validate_id(_id: Union[UUID, bytes, int, str], key: str):
    try: 
        if _id is None:
            return _id
        if isinstance(_id, UUID):
            return _id.bytes
        if isinstance(_id, bytes):
            return UUID(bytes=_id).bytes
        if isinstance(_id, int):
            return UUID(int=_id).bytes
        return UUID(_id).bytes
    except AttributeError:
        raise TypeError
