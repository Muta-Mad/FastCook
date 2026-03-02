from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.cart.models import ShoppingCart
from api.favorite.models import Favorite
from api.recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from api.users.models import User


def recipe_relations():
    return (
        selectinload(Recipe.author),
        selectinload(Recipe.tags),
        selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient),
    )

def get_recipes_query(
    current_user: User | None = None,
    is_favorited: bool | None = None,
    is_in_shopping_cart: bool | None = None,
    author: int | None = None,
    tags: list[str] | None = None,
):
    query = select(Recipe).options(*recipe_relations())
    if author:
        query = query.where(Recipe.author_id == author)
    if tags:
        query = query.join(Recipe.tags).where(Tag.slug.in_(tags))

    if is_favorited and current_user:
        query = query.join(Favorite).where(
            Favorite.user_id == current_user.id
        )
    if is_in_shopping_cart and current_user:
        query = query.join(ShoppingCart).where(
            ShoppingCart.user_id == current_user.id
        )
    return query.order_by(Recipe.id).distinct()

def get_recipe_query(id: int):
    return (
        select(Recipe)
        .options(
            *recipe_relations()
        )
        .where(Recipe.id==id)
    )

def get_tags_query():
    return select(Tag).order_by(Tag.id)

def get_tag_query(id):
    return select(Tag).where(Tag.id == id)

def get_ingredients_query():
    return select(Ingredient).order_by(Ingredient.id)

def get_ingredient_query(id):
    return select(Ingredient).where(Ingredient.id == id)

