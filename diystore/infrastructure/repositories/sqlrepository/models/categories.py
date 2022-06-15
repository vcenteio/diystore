from uuid import UUID

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import BINARY
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates

from ..base import Base


class CategoryOrmModel:
    @validates("id", "parent_id")
    def _validate_id(self, key, _id):
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

    @validates("parent")
    def _validate_parent(self, key, parent):
        if not isinstance(parent, self._parent_type):
            raise TypeError(f"{key} must be a {self._parent_type.__name__} object")
        return parent

    @validates("children")
    def _validate_children(self, key, child):
        if not isinstance(child, self._children_type):
            raise TypeError(f"{key} must be {self._children_type.__name__} objects")
        return child


class TopLevelCategoryOrmModel(CategoryOrmModel, Base):
    __tablename__ = "toplevel_category"

    id = Column(BINARY(16), primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(3000))

    children = relationship("MidLevelCategoryOrmModel", back_populates="parent")

    @property
    def _children_type(self):
        return MidLevelCategoryOrmModel

    def __repr__(self):
        return (
            f"TopLevelCategoryOrmModel(id={UUID(bytes=self.id)}, name={self.name!r}, "
            f"description={self.description!r})"
        )


class MidLevelCategoryOrmModel(CategoryOrmModel, Base):
    __tablename__ = "midlevel_category"

    id = Column(BINARY(16), primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(300))
    parent_id = Column(BINARY(16), ForeignKey("toplevel_category.id"), nullable=False)

    parent = relationship("TopLevelCategoryOrmModel", back_populates="children")
    children = relationship("TerminalCategoryOrmModel", back_populates="parent")

    @property
    def _parent_type(self):
        return TopLevelCategoryOrmModel

    @property
    def _children_type(self):
        return TerminalCategoryOrmModel

    def __repr__(self):
        return (
            f"MidLevelCategoryOrmModel(id={UUID(bytes=self.id)}, name={self.name!r}, "
            f"description={self.description!r}, parent_id={self.parent_id!r})"
        )


class TerminalCategoryOrmModel(CategoryOrmModel, Base):
    __tablename__ = "terminal_category"

    id = Column(BINARY(16), primary_key=True)
    name = Column(String(50))
    description = Column(String(300))
    parent_id = Column(BINARY(16), ForeignKey("midlevel_category.id"))

    parent = relationship("MidLevelCategoryOrmModel", back_populates="children")

    @property
    def _parent_type(self):
        return MidLevelCategoryOrmModel

    def __repr__(self):
        return (
            f"TerminalCategoryOrmModel(id={UUID(bytes=self.id)}, name={self.name!r}, "
            f"description={self.description!r}, parent_id={self.parent_id!r})"
        )
