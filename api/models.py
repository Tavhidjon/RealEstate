from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, blank=True, null=True, 
                               related_name='representatives')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        if self.company:
            return f"{self.email} (Company Owner: {self.company.name})"
        return self.email
        
    @property
    def is_company_owner(self):
        """Check if user is a company owner/representative"""
        return self.company is not None


class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='building_images/', blank=True, null=True)  # Main image
    latitude = models.FloatField(help_text="Latitude coordinate")
    longitude = models.FloatField(help_text="Longitude coordinate")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='buildings')
    floors_count = models.PositiveIntegerField()
    flats_count = models.PositiveIntegerField()
    model_3d = models.FileField(
        upload_to='3d_models/',
        validators=[FileExtensionValidator(allowed_extensions=['gltf', 'glb', 'obj'])],
        help_text="Upload 3D model (GLTF, GLB, OBJ)",
        blank=True,
        null=True
    )


    def __str__(self):
        return self.name


class BuildingImage(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(
        upload_to='building_images/',
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])],
        help_text="Optional. Upload an image for the building (JPEG, PNG, GIF, WEBP)"
    )
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order to display the images")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.building.name} - {self.id}"


class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.PositiveIntegerField(help_text="0 = Ground floor, 1 = First floor, etc.")
    plan_image = models.ImageField(upload_to='floor_plans/')

    class Meta:
        unique_together = ('building', 'floor_number')
        ordering = ['floor_number']

    def __str__(self):
        return f"{self.building.name} - Floor {self.floor_number}"


class Flat(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='flats')
    number = models.CharField(max_length=10, help_text="Flat number or label (e.g., 2A, 2B)")
    area = models.FloatField(help_text="Area in square meters")

    class Meta:
        unique_together = ('floor', 'number')

    def __str__(self):
        return f"Flat {self.number} on Floor {self.floor.floor_number} ({self.floor.building.name})"


class Chat(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='chats')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'company')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat between {self.user.username} and {self.company.name}"


class Message(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('company', 'Company'),
    )
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message in {self.chat} at {self.timestamp}"



