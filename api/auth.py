from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom Token serializer that works with email as USERNAME_FIELD
    """
    username_field = 'email'
    
    def validate(self, attrs):
        # Handle both email and username fields
        if 'username' in attrs and 'email' not in attrs:
            attrs['email'] = attrs['username']
            
        return super().validate(attrs)


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that uses the email-aware serializer
    """
    serializer_class = EmailTokenObtainPairSerializer
