from rest_framework import serializers
from .models import Company, Building, Floor, Flat, AppUser, BuildingImage
from rest_framework.validators import UniqueValidator


# User Serializers
class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=AppUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = AppUser
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 field as it's only used for validation
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        # Extract other fields
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        
        # Create a new user using create_user manager method which handles passwords properly
        user = AppUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            **validated_data  # Pass all remaining fields directly
        )
        
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AppUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 
                  'profile_picture', 'is_verified', 'date_joined', 'is_active', 'company', 'company_name')
        read_only_fields = ('is_verified', 'date_joined', 'is_active', 'company_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        
        # Only show admin fields to admin users
        if request and request.user and not (request.user.is_staff or request.user.is_superuser):
            admin_fields = ['is_active', 'company', 'company_name']
            for field in admin_fields:
                if field in self.fields:
                    self.fields.pop(field)
    
    def get_company_name(self, obj):
        if obj.company:
            return obj.company.name
        return None


class AdminUserListSerializer(UserDetailSerializer):
    """Enhanced serializer for admin view of all users"""
    last_login_display = serializers.SerializerMethodField()
    chat_count = serializers.SerializerMethodField()
    
    class Meta(UserDetailSerializer.Meta):
        fields = UserDetailSerializer.Meta.fields + ('is_staff', 'is_superuser', 'last_login', 
                                                    'last_login_display', 'chat_count')
        read_only_fields = UserDetailSerializer.Meta.read_only_fields + ('last_login', 'last_login_display', 'chat_count')
    
    def get_last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M:%S')
        return "Never"
    
    def get_chat_count(self, obj):
        return obj.chats.count()


# Company Serializer
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


# BuildingImage Serializer
class BuildingImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  # Make image optional
    
    class Meta:
        model = BuildingImage
        fields = ('id', 'building', 'image', 'caption', 'order')
        
    def validate_image(self, value):
        """
        Check that the image file is valid and not too large.
        """
        if value is None:
            return value
            
        # Check file size (limit to 5MB)
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError("Image file too large. Size should not exceed 5MB.")
            
        return value
        

# Building Serializer
class BuildingSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(required=False, read_only=True)
    additional_images = BuildingImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Building
        fields = '__all__'


# Floor Serializer
class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = '__all__'


# Flat Serializer
class FlatSerializer(serializers.ModelSerializer):
    building_name = serializers.SerializerMethodField()
    floor_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Flat
        fields = '__all__'
        
    def get_building_name(self, obj):
        return obj.floor.building.name
        
    def get_floor_number(self, obj):
        return obj.floor.floor_number


# Chat serializers have been moved to chat_serializers.py
