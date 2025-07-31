from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that accepts email instead of username
    """
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['name'] = user.get_full_name()
        
        # Add company information if user is linked to a company
        if user.company:
            token['company_id'] = user.company.id
            token['company_name'] = user.company.name
            token['is_company_owner'] = True
        else:
            token['is_company_owner'] = False
        
        return token


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Takes a set of user credentials (email/password) and returns an access and refresh JWT pair
    """
    serializer_class = EmailTokenObtainPairSerializer
