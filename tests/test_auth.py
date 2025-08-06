
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to the Python path to allow importing 'auth'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the streamlit module before it's imported by our 'auth' module.
# This prevents errors when tests are run outside of a Streamlit app context.
mock_st = MagicMock()
mock_st.session_state = {}
sys.modules['streamlit'] = mock_st
sys.modules['auth.st'] = mock_st


from auth import create_user, login_user

class TestAuth(unittest.TestCase):

    def setUp(self):
        """
        Clear the mock session_state and reset mock call counts before each test.
        """
        mock_st.session_state.clear()
        mock_st.reset_mock()

    @patch('auth.db')
    @patch('auth.firebase_admin.auth')
    def test_create_user_success(self, mock_auth, mock_db):
        """Test successful user creation."""
        mock_user = MagicMock()
        mock_user.uid = 'test_uid'
        mock_auth.create_user.return_value = mock_user

        user = create_user('test@example.com', 'password123')

        self.assertIsNotNone(user)
        self.assertEqual(user.uid, 'test_uid')
        mock_auth.create_user.assert_called_once_with(email='test@example.com', password='password123')
        mock_db.collection.return_value.document.assert_called_once_with('test_uid')
        mock_st.success.assert_called_once_with(f"Successfully created user: {mock_user.uid}")

    @patch('auth.firebase_admin.auth')
    def test_create_user_failure(self, mock_auth):
        """Test user creation failure."""
        exception_message = "Email already exists"
        mock_auth.create_user.side_effect = Exception(exception_message)

        user = create_user('test@example.com', 'password123')

        self.assertIsNone(user)
        mock_auth.create_user.assert_called_once_with(email='test@example.com', password='password123')
        mock_st.error.assert_called_once_with(f"Error creating user: {exception_message}")

    @patch('auth.firebase_admin.auth')
    def test_login_user_success(self, mock_auth):
        """Test successful user login."""
        mock_user = MagicMock()
        mock_user.uid = 'test_uid'
        mock_auth.get_user_by_email.return_value = mock_user

        user = login_user('test@example.com', 'password123')

        self.assertIsNotNone(user)
        self.assertEqual(user.uid, 'test_uid')
        self.assertTrue(mock_st.session_state['logged_in'])
        self.assertEqual(mock_st.session_state['user'], 'test_uid')
        mock_auth.get_user_by_email.assert_called_once_with('test@example.com')

    @patch('auth.firebase_admin.auth')
    def test_login_user_failure(self, mock_auth):
        """Test user login failure."""
        exception_message = "User not found"
        mock_auth.get_user_by_email.side_effect = Exception(exception_message)

        user = login_user('test@example.com', 'password123')

        self.assertIsNone(user)
        self.assertIn('logged_in', mock_st.session_state)
        self.assertFalse(mock_st.session_state['logged_in'])
        mock_auth.get_user_by_email.assert_called_once_with('test@example.com')
        mock_st.error.assert_called_once_with(f"Error logging in: {exception_message}")

if __name__ == '__main__':
    unittest.main()
