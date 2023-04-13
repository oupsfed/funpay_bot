from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (FollowingLotViewSet, GameViewSet, ItemViewSet, LotViewSet,
                    ServerViewSet, UserViewSet)

app_name = 'api'

router = SimpleRouter()
router.register('games', GameViewSet)
router.register('items', ItemViewSet)
router.register('lots', LotViewSet)
router.register('users', UserViewSet)
router.register('following', FollowingLotViewSet)
router.register('servers', ServerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
