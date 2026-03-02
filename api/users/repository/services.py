from api.core.exceptions import GlobalError
from api.users.models import Follow
from api.users.repository.queries import get_user_by_id, get_follow_query

async def subscribe_user(session, current_user, author_id):
    if current_user.id == author_id:
        raise GlobalError.bad_request('Нельзя подписываться на самого себя')

    result = await session.execute(get_user_by_id(author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise GlobalError.not_found('Пользователь не найден')

    existing = await session.execute(
        get_follow_query(current_user.id, author_id)
    )
    if existing.scalar_one_or_none():
        raise GlobalError.bad_request('Вы уже подписаны')

    follow = Follow(
        follower_id=current_user.id,
        author_id=author_id
    )
    session.add(follow)
    await session.commit()

    return author


async def unsubscribe_user(session, current_user, author_id):
    result = await session.execute(get_user_by_id(author_id))
    if not result.scalar_one_or_none():
        raise GlobalError.not_found('Пользователь не найден')

    result = await session.execute(
        get_follow_query(current_user.id, author_id)
    )
    follow = result.scalar_one_or_none()
    if not follow:
        raise GlobalError.bad_request('Подписка не найдена')

    await session.delete(follow)
    await session.commit()