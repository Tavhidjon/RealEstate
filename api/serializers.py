from rest_framework import serializers
from .models import Company, Building, Floor, Flat, AppUser
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
    class Meta:
        model = AppUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 
                  'profile_picture', 'is_verified', 'date_joined')
        read_only_fields = ('is_verified', 'date_joined')


# Company Serializer
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


# Building Serializer
class BuildingSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(required=False, read_only=True)
    
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
