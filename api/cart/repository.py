from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.cart.schemas import RecipeShort
from api.cart.models import ShoppingCart
from api.recipes.models import Ingredient, Recipe, RecipeIngredient


def get_shopping_cart_query(id, current_user):
    return select(ShoppingCart).where(ShoppingCart.recipe_id == id, ShoppingCart.user_id == current_user.id)

def get_recipe(recipe_id):
    return select(Recipe).where(Recipe.id == recipe_id)

def short_recipe(recipe):
    return RecipeShort(
        id=recipe.id,
        name=recipe.name,
        image=recipe.image,
        cooking_time=recipe.cooking_time
    )

async def get_shopping_cart_ingredients(
    user_id: int,
    session: AsyncSession,
):
    result = await session.execute(
        select(
            Ingredient.name,
            Ingredient.measurement_unit,
            func.sum(RecipeIngredient.amount).label('total_amount'),
        )
        .join(RecipeIngredient, RecipeIngredient.ingredient_id == Ingredient.id)
        .join(Recipe, Recipe.id == RecipeIngredient.recipe_id)
        .join(ShoppingCart, ShoppingCart.recipe_id == Recipe.id)
        .where(ShoppingCart.user_id == user_id)
        .group_by(Ingredient.name, Ingredient.measurement_unit)
        .order_by(Ingredient.name)
    )
    return result.all()