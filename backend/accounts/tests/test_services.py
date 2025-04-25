from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from accounts.services import create_user_with_group

User = get_user_model()

class CreateUserWithGroupTests(TestCase):
    def test_create_user_assigns_existing_group(self):
        # Create a group first
        merchant_group = Group.objects.create(name='Merchant')

        # Test data
        email = 'merchant@test.com'
        password = 'foo'
        role = 'merchant'

        # Create user with group
        user = create_user_with_group(
            email=email,
            password=password,
            role=role
        )

        # Assertions
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.role, role)
        self.assertTrue(user.groups.filter(name='Merchant').exists())
        self.assertEqual(user.groups.count(), 1)

    def test_create_user_creates_missing_group(self):
        # Test data
        email = 'user@test.com'
        password = 'foo'
        role = 'user'

        # Create user with non-existent group
        user = create_user_with_group(
            email=email,
            password=password,
            role=role
        )

        # Assertions
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.role, role)
        self.assertTrue(Group.objects.filter(name='User').exists())
        self.assertTrue(user.groups.filter(name='User').exists())
        self.assertEqual(user.groups.count(), 1)