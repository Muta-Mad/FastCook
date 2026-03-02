from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint

from api.core.basemodel import Base
from api.core.idmixin import IdPkMixin


class Favorite(Base, IdPkMixin):
    """Модель избранного"""
    __tablename__ = 'favorites'
    __table_args__ = (
        UniqueConstraint(
        'user_id', 'recipe_id', 
        name='unique_favorite'),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            'users.id', 
            ondelete='CASCADE')
        )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey(
            'recipes.id', 
            ondelete='CASCADE')
        )
    recipe = relationship('Recipe',
        back_populates='favorites',
    )
    user = relationship(
        'User', 
        back_populates='favorites',
    )