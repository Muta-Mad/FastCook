from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint

from api.core.basemodel import Base
from api.core.idmixin import IdPkMixin


class ShoppingCart(Base, IdPkMixin):
    """Модель корзины"""
    __tablename__ = 'shopping_carts'
    __table_args__ = (
        UniqueConstraint(
        'user_id', 'recipe_id', 
        name='unique_cart_item'),
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
        back_populates='shopping_carts',
    )
    user = relationship(
        'User', 
        back_populates='shopping_carts',
    )
