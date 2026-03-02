from api.users.repository.repository import get_recipe_subscribers
from api.users.schemas import SubscribeSchemas


async def get_subscribe_schema(author, session, recipes_limit=None):
    recipes = await get_recipe_subscribers(session, author.id, recipes_limit)
    return SubscribeSchemas(
        id=author.id,
        email=author.email,
        username=author.username,
        first_name=author.first_name,
        last_name=author.last_name,
        avatar=author.avatar,
        is_subscribed=True,
        recipes=recipes,
        recipes_count=len(recipes)
    )
