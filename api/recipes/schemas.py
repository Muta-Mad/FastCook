from pydantic import BaseModel, Field, ConfigDict

from api.users.schemas import UserRead

class IngredientInRecipe(BaseModel):
    id: int
    name: str
    measurement_unit: str
    amount: int


class IngredientInRecipeCreate(BaseModel):
    id: int
    amount: int = Field(gt=0, description='Колличесво должно быть не меньше 1')


class RecipeRead(BaseModel):
    id: int
    tags: list['TagRead']
    author: UserRead
    ingredients: list[IngredientInRecipe]
    name: str
    image: str | None = None
    text: str
    cooking_time: int
    is_favorited: bool
    is_in_shopping_cart: bool


class RecipeCreate(BaseModel):
    ingredients: list['IngredientInRecipeCreate'] = Field(min_length=1)
    tags: list[int] = Field(min_length=1)
    image: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=256)
    text: str = Field(min_length=1)
    cooking_time: int = Field(gt=0, description='Время готовки не должно быть не меньше 1')


class RecipeUpdate(BaseModel):
    ingredients: list['IngredientInRecipeCreate'] = Field(min_length=1)
    tags: list[int] = Field(min_length=1)
    image: str | None = Field(default=None, min_length=1)
    name: str | None = Field(default=None, min_length=1, max_length=256)
    text: str | None = Field(default=None, min_length=1)
    cooking_time: int | None = Field(default=None, gt=0, description='Время готовки не должно быть не меньше 1')


class TagRead(BaseModel):
    id: int
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


class IngredientRead(BaseModel):
    id: int
    name: str
    measurement_unit: str

    model_config = ConfigDict(from_attributes=True)
