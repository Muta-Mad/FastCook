from sqlalchemy import select

from api.users.models import Follow, User
from api.users.schemas import UserCreate


def get_user_by_id(user_id: int):
    return select(User).where(User.id == user_id)

def get_follow_query(follower_id: int, author_id: int):
    return select(Follow).where(
        Follow.follower_id == follower_id,
        Follow.author_id == author_id
    )

def get_user_subscriptions_query(user_id: int):
    return (
        select(User)
        .join(Follow, User.id == Follow.author_id)
        .where(Follow.follower_id == user_id)
    )

def created_user(
        user_create: UserCreate,
):
    return select(User).where(User.username == user_create.username)