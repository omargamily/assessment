from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status

User = get_user_model()

class UserRegistrationViewTests(APITestCase):
    def setUp(self):
        # Create necessary groups
        Group.objects.create(name='User')
        Group.objects.create(name='Merchant')
        Group.objects.create(name='Staff')

    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'role': 'user'
        }
        response = self.client.post(reverse('accounts:register'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email', response.data)
        self.assertIn('role', response.data)
        self.assertNotIn('password', response.data)
        
        # Verify user was created in database
        user = User.objects.get(email=data['email'])
        self.assertEqual(user.role, 'user')
        self.assertTrue(user.groups.filter(name='User').exists())

    def test_register_merchant_success(self):
        """Test successful merchant registration"""
        data = {
            'email': 'merchant@example.com',
            'password': 'password123',
            'role': 'merchant'
        }
        response = self.client.post(reverse('accounts:register'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify merchant was created in database
        user = User.objects.get(email=data['email'])
        self.assertEqual(user.role, 'merchant')
        self.assertTrue(user.groups.filter(name='Merchant').exists())

    def test_register_missing_email(self):
        """Test registration with missing email"""
        data = {
            'password': 'password123',
            'role': 'user'
        }
        response = self.client.post(reverse('accounts:register'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_missing_password(self):
        """Test registration with missing password"""
        data = {
            'email': 'testuser@example.com',
            'role': 'user'
        }
        response = self.client.post(reverse('accounts:register'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_missing_role(self):
        """Test registration with missing role"""
        data = {
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        response = self.client.post(reverse('accounts:register'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_register_invalid_email_format(self):
        """Test registration with invalid email format"""
        data = {
            'email': 'invalid-email',
            'password': 'password123',
            'role': 'user'
        }
        response = self.client.post(reverse('accounts:register'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        data = {
            'email': 'duplicate@example.com',
            'password': 'password123',
            'role': 'user'
        }
        # First registration
        self.client.post(reverse('accounts:register'), data, format='json')
        
        # Second registration with same email
        response = self.client.post(reverse('accounts:register'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_get_not_allowed(self):
        """Test GET method not allowed"""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)