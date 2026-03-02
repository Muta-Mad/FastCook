from sqlalchemy import select

from api.favorite.models import Favorite


def get_favorite_query(id, current_user):
    return select(Favorite).where(Favorite.recipe_id == id, Favorite.user_id == current_user.id)
