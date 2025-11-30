from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Add custom claims to the JWT token."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        try:
            token['user_id'] = str(user.user_id)
        except Exception:
            token['user_id'] = None
        token['email'] = getattr(user, 'email', '')
        token['role'] = getattr(user, 'role', '')
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """View that returns token pair with custom claims."""
    serializer_class = CustomTokenObtainPairSerializer
