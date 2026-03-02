from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, UniqueConstraint, SmallInteger

from api.core.basemodel import Base
from api.core.idmixin import IdPkMixin
from api.users.models import User
from api.cart.models import ShoppingCart
from api.favorite.models import Favorite


class Recipe(IdPkMixin, Base):
    """Модель рецепта"""
    __tablename__ = 'recipes'
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    author: Mapped['User'] = relationship(back_populates='recipes')
    name: Mapped[str] = mapped_column(String(length=256))
    image: Mapped[str | None]
    ingredients: Mapped[list['Ingredient']] = relationship(
        secondary='recipe_ingredients', 
        back_populates='recipes',
        viewonly=True
    )
    tags: Mapped[list['Tag']] = relationship(
        secondary='recipe_tags', 
        back_populates='recipes',
        viewonly=True
    )
    text: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(SmallInteger)

    recipe_ingredients: Mapped[list['RecipeIngredient']] = relationship(
        'RecipeIngredient',
        cascade='all, delete-orphan',
        back_populates='recipe'
    )

    recipe_tags: Mapped[list['RecipeTag']] = relationship(
        'RecipeTag',
        cascade='all, delete-orphan',
        back_populates='recipe',
    )
    shopping_carts: Mapped[list['ShoppingCart']] = relationship(
        'ShoppingCart', 
        back_populates='recipe',
        cascade='all, delete-orphan'
    )
    favorites: Mapped[list['Favorite']] = relationship(
        'Favorite', 
        back_populates='recipe',
        cascade='all, delete-orphan'
    )


class Tag(IdPkMixin, Base):
    """Модель тега"""
    __tablename__ = 'tags'
    name: Mapped[str] = mapped_column(String(32))
    slug: Mapped[str] = mapped_column(
        String(64),
        unique=True,
    )
    recipes: Mapped[list['Recipe']] = relationship(
        secondary='recipe_tags',
        back_populates='tags'
    )
    

class Ingredient(IdPkMixin, Base):
    """Модель Ингредиента"""
    __tablename__ = 'ingredients'
    __table_args__ = (
        UniqueConstraint('name', 'measurement_unit', name='unique_ingredient'),
    )
    name: Mapped[str] = mapped_column(String(length=128))
    measurement_unit: Mapped[str] = mapped_column(String(length=64))
    recipes: Mapped[list['Recipe']] = relationship(
        secondary='recipe_ingredients',
        back_populates='ingredients'
    )


class RecipeIngredient(IdPkMixin, Base):
    """Модель для связи рецепта и ингредиента"""
    __tablename__ = 'recipe_ingredients'
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipes.id', ondelete='CASCADE'))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredients.id', ondelete='CASCADE'))
    amount: Mapped[int] = mapped_column(SmallInteger)
    ingredient: Mapped['Ingredient'] = relationship()
    recipe: Mapped['Recipe'] = relationship(
        back_populates='recipe_ingredients'
    )


class RecipeTag(Base):
    """Модель для связи рецепта и тега"""
    __tablename__ = 'recipe_tags'
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    tag: Mapped['Tag'] = relationship()
    recipe: Mapped['Recipe'] = relationship(
        back_populates='recipe_tags'
    )
