# accounts/models.py
import uuid  # Add this import
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        # Ensure id is not passed in extra_fields if it's auto-generated
        extra_fields.pop('id', None)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'staff')
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        # Ensure id is not passed in extra_fields if it's auto-generated
        extra_fields.pop('id', None)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('merchant', 'Merchant'),
        ('user', 'User'),
        ('staff', 'Staff'),
    ]

    # Add the UUID primary key field
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Use group-based authorization - staff access granted to superusers and members of Staff group
        return self.is_superuser or self.groups.filter(name='Staff').exists()

