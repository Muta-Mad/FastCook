from fastapi import APIRouter, Depends, Request, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.cart.repository import get_shopping_cart_ingredients
from api.core.base_paginator import Paginator
from api.core.exceptions import GlobalError
from api.core.paginate_schemas import Page
from api.dependencies import get_current_user, get_current_user_optional
from api.recipes.models import Recipe

from api.recipes.repository.flags import get_user_recipe_flags
from api.recipes.repository.mappers import map_recipe_to_read
from api.recipes.repository.mutations import set_recipe_ingredients, set_recipe_tags
from api.recipes.repository.queries import get_recipes_query
from api.recipes.repository.services import get_full_recipe, get_owned_recipe
from api.recipes.repository.validators import validate_ingredients, validate_tags
from api.recipes.schemas import RecipeCreate, RecipeRead, RecipeUpdate
from api.core.database import get_db
from api.users.models import User


router = APIRouter(prefix='/recipes', tags=['Recipes'])

@router.get('/', response_model=Page[RecipeRead])
async def get_recipes(
    paginator: Paginator = Depends(),
    session: AsyncSession = Depends(get_db),
    current_user: User  = Depends(get_current_user_optional),
    is_favorited: bool | None = Query(None),
    is_in_shopping_cart: bool | None = Query(None),
    author: int | None = Query(None),
    tags: list[str] | None = Query(None),
):
    query = get_recipes_query(
        current_user=current_user,
        is_favorited=is_favorited,
        is_in_shopping_cart=is_in_shopping_cart,
        author=author,
        tags=tags
    )
    paginated_data = await paginator.get_paginate(
        session=session,
        model=Recipe,
        base_query=query
    )
    recipes = paginated_data['results']
    recipe_ids = [recipe.id for recipe in recipes]
    favorites_set = set()
    cart_set = set()
    if current_user and recipe_ids:
        favorites_set, cart_set = await get_user_recipe_flags(
            session=session, user_id=current_user.id, recipe_ids=recipe_ids
        )
    recipes_out = [
        map_recipe_to_read(recipe, favorites_set, cart_set)
        for recipe in recipes
    ]
    return Page(
        count=paginated_data['count'],
        next=paginated_data['next'],
        previous=paginated_data['previous'],
        results=recipes_out
    )

@router.get('/download_shopping_cart/')
async def download_shopping_cart(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    ingredients = await get_shopping_cart_ingredients(
        current_user.id,
        session
    )
    lines = []
    for name, unit, total_amount in ingredients:
        line = f'- {name}: {total_amount} {unit}'
        lines.append(line)
    shopping_list_text = '\n'.join(lines)
    return Response(
        content=shopping_list_text,
        media_type="text/plain",
        headers={
            'Content-Disposition': 'attachment; filename=shopping_list.txt'
        }
    )

@router.get('/{id}/', response_model=RecipeRead)
async def get_recipe(
    id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User  = Depends(get_current_user_optional),
) -> RecipeRead: 
    recipe = await get_full_recipe(session, id)
    if not recipe:
        GlobalError.not_found('Рецепт с таким id не найден')
    favorites_set = set()
    cart_set = set()
    if current_user:
        favorites_set, cart_set = await get_user_recipe_flags(
            session=session, user_id=current_user.id, recipe_ids=[recipe.id]
        )
    return map_recipe_to_read(recipe, favorites_set, cart_set)

@router.delete('/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = await get_owned_recipe(session, id, current_user.id)
    await session.delete(recipe)
    await session.commit()

@router.post('/', response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def recipe_create(
    data: RecipeCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ):
    await validate_ingredients(session, data.ingredients)
    await validate_tags(session, data.tags)
    recipe = Recipe(
        author_id=current_user.id, 
        name=data.name, 
        image=data.image, 
        text=data.text, 
        cooking_time=data.cooking_time
    )
    session.add(recipe)
    await session.flush()
    await set_recipe_ingredients(session, recipe, data.ingredients)
    await set_recipe_tags(session, recipe, data.tags)
    await session.commit()
    recipe_to_read = await get_full_recipe(session=session, recipe_id=recipe.id)
    return map_recipe_to_read(recipe_to_read, favorites_set=set(), cart_set=set(),)

@router.patch('/{id}/', response_model=RecipeRead)
async def recipe_update(
    id: int,
    new_data: RecipeUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await validate_ingredients(session, new_data.ingredients)
    await validate_tags(session, new_data.tags)
    recipe = await get_owned_recipe(session, id, current_user.id)
    if new_data.name is not None:
        recipe.name = new_data.name
    if new_data.text is not None:
        recipe.text = new_data.text
    if new_data.image is not None:
        recipe.image = new_data.image
    if new_data.cooking_time is not None:
        recipe.cooking_time = new_data.cooking_time
    if new_data.ingredients is not None:
        await set_recipe_ingredients(session, recipe, new_data.ingredients)
    if new_data.tags is not None:
        await set_recipe_tags(session, recipe, new_data.tags)
    await session.commit()
    recipe_to_read = await get_full_recipe(session=session, recipe_id=recipe.id)
    favorites_set, cart_set = await get_user_recipe_flags(
        session=session, 
        user_id=current_user.id, 
        recipe_ids=[recipe.id]
    )
    return map_recipe_to_read(recipe_to_read, favorites_set=favorites_set,cart_set=cart_set)

@router.get('/{id}/get-link/')
async def get_short_link(
    id: int,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    recipe = await get_full_recipe(session, id)
    short_link = str(request.url_for(
        'redirect_short_link',
        id=recipe.id
    ))
    return {'short-link': short_link}
