from uuid import UUID

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import BINARY
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates

from . import Base
from ..helpers import validate_id
from ..exceptions import OrmEntityNotFullyLoaded
from .....domain.entities.product import TopLevelProductCategory
from .....domain.entities.product import MidLevelProductCategory
from .....domain.entities.product import TerminalLevelProductCategory


class CategoryOrmModel:
    @validates("id", "parent_id")
    def _validate_id(self, key, _id):
        return validate_id(_id, key)

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

    def to_domain_entity(self) -> TopLevelProductCategory:
        return TopLevelProductCategory(
            id=UUID(bytes=self.id), name=self.name, description=self.description
        )

    @classmethod
    def from_domain_entity(
        cls, entity: TopLevelProductCategory
    ) -> "TopLevelCategoryOrmModel":
        if not isinstance(entity, TopLevelProductCategory):
            raise TypeError(f"entity must be {cls.__name__} type")
        return cls(id=entity.id, name=entity.name, description=entity.description)

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

    def to_domain_entity(self) -> MidLevelProductCategory:
        if self.parent is None:
            raise OrmEntityNotFullyLoaded
        return MidLevelProductCategory(
            id=UUID(bytes=self.id),
            name=self.name,
            description=self.description,
            parent=self.parent.to_domain_entity(),
        )

    @classmethod
    def from_domain_entity(
        cls, entity: MidLevelProductCategory
    ) -> "MidLevelCategoryOrmModel":
        if not isinstance(entity, MidLevelProductCategory):
            raise TypeError(f"entity must be {cls.__name__} type")
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            parent_id=entity.get_parent_id(),
        )

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
    products = relationship("ProductOrmModel", back_populates="category")

    @property
    def _parent_type(self):
        return MidLevelCategoryOrmModel

    def to_domain_entity(self) -> TerminalLevelProductCategory:
        if self.parent is None:
            raise OrmEntityNotFullyLoaded
        return TerminalLevelProductCategory(
            id=UUID(bytes=self.id),
            name=self.name,
            description=self.description,
            parent=self.parent.to_domain_entity(),
        )

    @classmethod
    def from_domain_entity(
        cls, entity: TerminalLevelProductCategory
    ) -> "TerminalCategoryOrmModel":
        if not isinstance(entity, TerminalLevelProductCategory):
            raise TypeError(f"entity must be TerminalLevelProductCategory type")
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            parent_id=entity.get_parent_id(),
        )

    def __repr__(self):
        return (
            f"TerminalCategoryOrmModel(id={UUID(bytes=self.id)}, name={self.name!r}, "
            f"description={self.description!r}, parent_id={self.parent_id!r})"
        )