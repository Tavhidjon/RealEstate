from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    CompanyViewSet, BuildingViewSet, FloorViewSet, FlatViewSet,
    RegisterView, UserDetailView, logout_view, protected_example_view,
    admin_panel_view
)
from .auth import EmailTokenObtainPairView
from .root_view import ApiRootView
from .auth_instructions import AuthInstructionsView

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'buildings', BuildingViewSet)
router.register(r'floors', FloorViewSet)
router.register(r'flats', FlatViewSet)

auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', logout_view, name='logout'),
    path('profile/', UserDetailView.as_view(), name='user-detail'),
    # Add a debug endpoint for easier testing
    path('debug-register/', RegisterView.as_view(), name='debug-register'),
]

urlpatterns = [
    path('', ApiRootView.as_view(), name='api-root'),  # Custom API root view
    path('', include(router.urls)),
    path('auth/', include(auth_urlpatterns)),
    path('example/protected/', protected_example_view, name='protected-example'),
    path('auth/help/', AuthInstructionsView.as_view(), name='auth-instructions'),
    path('admin/panel/', admin_panel_view, name='admin-panel'),
]
