from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter(tags=['Recipes'])


@router.get('/s/{id}', name='redirect_short_link')
def redirect_short_link(id: int):
    """Перенаправляет по короткой ссылки"""
    return RedirectResponse(url=f'/recipes/{id}')

