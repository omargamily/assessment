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
        
class BaseAuthTestCase(APITestCase):
    """Base class for tests needing an authenticated user."""
    def setUp(self):
        self.email = 'testbase@example.com'
        self.password = 'password123'
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            role='user'
        )

class TokenObtainPairViewTests(BaseAuthTestCase):
    """Tests for the sign-in view."""
    def test_signin_success(self):
        url = reverse('accounts:token_obtain_pair')
        data = {'email': self.email, 'password': self.password}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class TokenRefreshViewTests(BaseAuthTestCase):
    """Tests for the token refresh view."""
    def setUp(self):
        super().setUp()
        signin_url = reverse('accounts:token_obtain_pair')
        signin_data = {'email': self.email, 'password': self.password}
        signin_response = self.client.post(signin_url, signin_data, format='json')
        if signin_response.status_code == status.HTTP_200_OK:
             self.refresh_token = signin_response.data.get('refresh')
        else:
             self.fail(f"Failed to sign in during setUp for TokenRefreshViewTests. Status: {signin_response.status_code}, Data: {signin_response.data}")
        # Ensure refresh token was actually obtained
        if not hasattr(self, 'refresh_token') or not self.refresh_token:
            self.fail("Refresh token not obtained during setUp for TokenRefreshViewTests.")


    def test_token_refresh_success(self):
        url = reverse('accounts:token_refresh')
        if not hasattr(self, 'refresh_token') or not self.refresh_token:
             self.fail("Cannot run test_token_refresh_success: refresh_token not set in setUp.")
        data = {'refresh': self.refresh_token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class UserListViewTests(APITestCase):
    def setUp(self):
        # Create necessary groups
        self.merchant_group = Group.objects.create(name='Merchant')
        self.user_group = Group.objects.create(name='User')

        # Create a merchant user
        self.merchant = User.objects.create_user(
            email='merchant@test.com',
            password='password123',
            role='merchant'
        )
        self.merchant.groups.add(self.merchant_group)

        # Create regular users
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='password123',
            role='user'
        )
        self.user1.groups.add(self.user_group)

        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='password123',
            role='user'
        )
        self.user2.groups.add(self.user_group)

        # URL for listing users
        self.url = reverse('accounts:user-list')

    def test_merchant_can_list_users(self):
        """Test that a merchant can successfully list all users"""
        self.client.force_authenticate(user=self.merchant)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return both users
        self.assertNotIn('password', response.data[0])  # Ensure password is not exposed
        
        # Verify the returned data contains our test users
        emails = [user['email'] for user in response.data]
        self.assertIn(self.user1.email, emails)
        self.assertIn(self.user2.email, emails)

    def test_user_cannot_list_users(self):
        """Test that a regular user cannot access the list users endpoint"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class MeViewTests(BaseAuthTestCase):
    """Tests for the /me endpoint."""

    def test_get_me_success(self):
        """Test authenticated user can retrieve their details."""
        url = reverse('accounts:me')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['role'], self.user.role)
        self.assertEqual(str(response.data['id']), str(self.user.id))
        self.assertIn('created_at', response.data)
        self.assertNotIn('password', response.data)

    def test_get_me_unauthenticated(self):
        """Test unauthenticated user cannot access /me."""
        url = reverse('accounts:me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)