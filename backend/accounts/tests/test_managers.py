from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

class UserManagerTests(TestCase):
    def test_create_user_successful(self):
        email = 'normal@user.com'
        password = 'foo'
        role = 'user'
        user = User.objects.create_user(
            email=email,
            password=password,
            role=role
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.role, role)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.has_usable_password())

    def test_create_user_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='foo', role='user')

    def test_create_superuser_successful(self):
        email = 'super@user.com'
        password = 'foo'
        user = User.objects.create_superuser(
            email=email,
            password=password
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.role, 'staff')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(password))

    def test_create_superuser_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='', password='foo')

    def test_create_superuser_with_is_superuser_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='test@test.com',
                password='foo',
                is_superuser=False
            )