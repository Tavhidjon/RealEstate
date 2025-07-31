from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    CompanyViewSet, BuildingViewSet, FloorViewSet, FlatViewSet,
    RegisterView, UserDetailView, AllUsersListView, logout_view, protected_example_view,
    admin_panel_view, ProfileRedirectView, BuildingImageViewSet
)
from .chat_views import ChatViewSet, CompanyChatListView, CompanyChatViewSet
from .company_owner_chat_views import (
    CompanyOwnerChatListView, CompanyOwnerChatDetailView,
    CompanyOwnerSendMessageView, CompanyOwnerGetUserListView
)
from .auth import EmailTokenObtainPairView
from .root_view import ApiRootView
from .auth_instructions import AuthInstructionsView
from .company_owner_views import CompanyOwnerRegisterView, CompanyOwnerListView

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'building-images', BuildingImageViewSet)
router.register(r'floors', FloorViewSet)
router.register(r'flats', FlatViewSet)
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'company-chats', CompanyChatViewSet, basename='company-chat')

auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', logout_view, name='logout'),
    path('profile/', UserDetailView.as_view(), name='user-detail'),
    # Admin-only endpoint to list all users
    path('users/all/', AllUsersListView.as_view(), name='all-users-list'),
    # Admin-only endpoints for company owners
    path('register-company-owner/', CompanyOwnerRegisterView.as_view(), name='register-company-owner'),
    path('company-owners/', CompanyOwnerListView.as_view(), name='company-owners-list'),
    # Add a debug endpoint for easier testing
    path('debug-register/', RegisterView.as_view(), name='debug-register'),
]

chat_urlpatterns = [
    path('companies-list/', CompanyChatListView.as_view(), name='chat-companies-list'),
    # Company Owner chat endpoints
    path('company-owner/chats/', CompanyOwnerChatListView.as_view(), name='company-owner-chats'),
    path('company-owner/chat/<int:pk>/', CompanyOwnerChatDetailView.as_view(), name='company-owner-chat-detail'),
    path('company-owner/chat/<int:chat_id>/send/', CompanyOwnerSendMessageView.as_view(), name='company-owner-send-message'),
    path('company-owner/users/', CompanyOwnerGetUserListView.as_view(), name='company-owner-users-with-chats'),
]

urlpatterns = [
    path('', ApiRootView.as_view(), name='api-root'),  # Custom API root view
    path('', include(router.urls)),
    path('auth/', include(auth_urlpatterns)),
    path('chat/', include(chat_urlpatterns)),
    path('example/protected/', protected_example_view, name='protected-example'),
    path('auth/help/', AuthInstructionsView.as_view(), name='auth-instructions'),
    path('admin/panel/', admin_panel_view, name='admin-panel'),
]
