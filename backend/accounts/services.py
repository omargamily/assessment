from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

def create_user_with_group(email, password, role):
    with transaction.atomic():
        # Create the user instance
        user = User.objects.create_user(
            email=email,
            password=password,
            role=role
        )

        # Map role to group name (they match in our case)
        group_name = role.capitalize()
        
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            # If the group doesn't exist, create it and add the user
            group = Group.objects.create(name=group_name)
            user.groups.add(group)

        return user