from django.test import TestCase
from accounts.serializers import UserRegistrationSerializer
from unittest.mock import patch


class UserRegistrationSerializerTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'user'
        }

    def test_serializer_valid_data(self):
        """Test serializer with valid data passes validation"""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], self.valid_data['email'])
        self.assertEqual(serializer.validated_data['role'], self.valid_data['role'])
        self.assertEqual(serializer.validated_data['password'], self.valid_data['password'])
        self.assertEqual(len(serializer.errors), 0)

    def test_serializer_invalid_email(self):
        """Test serializer with invalid email format"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_serializer_missing_email(self):
        """Test serializer with missing email field"""
        invalid_data = self.valid_data.copy()
        del invalid_data['email']
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_serializer_missing_password(self):
        """Test serializer with missing password field"""
        invalid_data = self.valid_data.copy()
        del invalid_data['password']
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_serializer_missing_role(self):
        """Test serializer with missing role field"""
        invalid_data = self.valid_data.copy()
        del invalid_data['role']
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)

    def test_serializer_invalid_role(self):
        """Test serializer with invalid role choice"""
        invalid_data = self.valid_data.copy()
        invalid_data['role'] = 'invalid_role'
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)

    def test_serializer_password_write_only(self):
        """Test that password field is write-only"""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('password', serializer.data)

    @patch('accounts.serializers.create_user_with_group')
    def test_serializer_create_calls_service(self, mock_create_service):
        """Test that create method calls the user creation service with correct data"""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        mock_create_service.assert_called_once_with(
            email=self.valid_data['email'],
            password=self.valid_data['password'],
            role=self.valid_data['role']
        )