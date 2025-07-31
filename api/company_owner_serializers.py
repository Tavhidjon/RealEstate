from rest_framework import serializers
from .models import AppUser, Company
from rest_framework.validators import UniqueValidator


class CompanyOwnerRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to create company owners.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=AppUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=True,
        help_text="Company that this user will own/represent"
    )

    class Meta:
        model = AppUser
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 
                  'phone_number', 'profile_picture', 'company')

    def create(self, validated_data):
        password = validated_data.pop('password')
        username = validated_data.get('username')
        email = validated_data.get('email')
        
        # Create a new user with is_staff=False but link to company
        user = AppUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            **validated_data
        )
        
        return user
