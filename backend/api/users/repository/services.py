from sqlalchemy.exc import IntegrityError

from api.core.exceptions import GlobalError
from api.users.models import Follow
from api.users.repository.queries import get_user_by_id, get_follow_query


async def subscribe_user(session, current_user, author_id):
    if current_user.id == author_id:
        GlobalError.bad_request('Нельзя подписываться на самого себя')

    result = await session.execute(get_user_by_id(author_id))
    author = result.scalar_one_or_none()
    if not author:
        GlobalError.not_found('Пользователь не найден')

    follow = Follow(follower_id=current_user.id, author_id=author_id)
    session.add(follow)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        GlobalError.bad_request('Вы уже подписаны')

    return author


async def unsubscribe_user(session, current_user, author_id):
    result = await session.execute(get_user_by_id(author_id))
    if not result.scalar_one_or_none():
        GlobalError.not_found('Пользователь не найден')

    result = await session.execute(get_follow_query(current_user.id, author_id))
    follow = result.scalar_one_or_none()
    if not follow:
        GlobalError.bad_request('Подписка не найдена')

    await session.delete(follow)
    await session.commit()