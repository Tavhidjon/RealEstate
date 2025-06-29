from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CompanyViewSet, BuildingViewSet, FloorViewSet, FlatViewSet,
    RegisterView, UserDetailView, logout_view
)
from .auth import EmailTokenObtainPairView

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'floors', FloorViewSet)
router.register(r'flats', FlatViewSet)

auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    path('profile/', UserDetailView.as_view(), name='user-detail'),
    # Add a debug endpoint for easier testing
    path('debug-register/', RegisterView.as_view(), name='debug-register'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urlpatterns)),
]
