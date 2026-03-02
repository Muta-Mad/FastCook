from fastapi import APIRouter

from api.users.auth.views import router as auth_router
from api.users.views import router as users_router
from api.recipes.recipes import router as recipe_router
from api.recipes.tags import router as tag_router
from api.recipes.ingredients import router as ingredients_router
from api.cart.cart import router as cart_router
from api.favorite.favorite import router as favorite_router
from api.recipes.redirect_short_link import router as redirect_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(recipe_router)
router.include_router(tag_router)
router.include_router(ingredients_router)
router.include_router(cart_router)
router.include_router(favorite_router)
router.include_router(redirect_router)
