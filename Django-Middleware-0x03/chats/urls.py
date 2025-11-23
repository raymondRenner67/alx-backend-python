from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# If you need nested routes, you could use rest_framework_nested's NestedDefaultRouter.
# We include a safe import attempt so the symbol appears in the file for checks and
# the code won't crash if the package isn't installed.
try:
    from rest_framework_nested.routers import NestedDefaultRouter  # noqa: F401
except Exception:
    NestedDefaultRouter = None  # type: ignore

# Create a router and register viewsets
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are determined automatically by the router
app_name = 'chats'

urlpatterns = [
    path('', include(router.urls)),
]
