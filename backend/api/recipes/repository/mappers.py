from api.recipes.models import Ingredient, Recipe, Tag
from api.recipes.schemas import IngredientInRecipe, IngredientRead, RecipeRead, TagRead
from api.users.models import User
from api.users.schemas import UserRead


def map_user_to_read(user: User, subscribed_ids: set[int] | None = None) -> UserRead:
    is_sub = user.id in subscribed_ids if subscribed_ids is not None else False
    return UserRead(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_subscribed=is_sub,
        avatar=user.avatar,
    )


def map_recipe_to_read(
    recipe: Recipe,
    favorites_set: set[int],
    cart_set: set[int],
    subscribed_ids: set[int] | None = None,
) -> RecipeRead:
    ingredients = [
        IngredientInRecipe(
            id=ri.ingredient.id,
            name=ri.ingredient.name,
            measurement_unit=ri.ingredient.measurement_unit,
            amount=ri.amount,
        )
        for ri in recipe.recipe_ingredients
    ]
    tags = [map_tag_to_read(tag) for tag in recipe.tags]
    author = map_user_to_read(recipe.author, subscribed_ids)
    return RecipeRead(
        id=recipe.id,
        author=author,
        tags=tags,
        ingredients=ingredients,
        name=recipe.name,
        image=recipe.image,
        text=recipe.text,
        cooking_time=recipe.cooking_time,
        is_favorited=recipe.id in favorites_set,
        is_in_shopping_cart=recipe.id in cart_set,
    )

def map_tag_to_read(tag: Tag) -> TagRead:
    return TagRead.model_validate(tag)

def map_ingredient_to_read(ingredient: Ingredient) -> IngredientRead:
    return IngredientRead.model_validate(ingredient)
