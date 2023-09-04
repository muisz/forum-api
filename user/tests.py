import json
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import NotFound

from .models import User
from .views import AuthUserView


class UserModelTest(TestCase):
    def setUp(self):
        pass

    def test_set_name_method(self):
        name = "Muhamad Abdul Muis"
        user = User()
        user.set_name(name)
        
        self.assertEqual(user.first_name, "Muhamad")
        self.assertEqual(user.last_name, "Abdul Muis")

    def test_register_method(self):
        user = User.register("Muhamad Abdul Muis", "abdulmuis", "password")
        
        self.assertIsInstance(user.id, int)
    
    def test_login_method(self):
        user = User.register("Muhamad Abdul Muis", "abdulmuis", "password")
        user_from_login = User.login(user.username, "password")

        self.assertEqual(user_from_login, user)
        self.assertTrue(hasattr(user_from_login, "token"))
    
    def test_inactivate_method(self):
        user = User.register("Muhamad Abdul Muis", "abdulmuis", "password")
        user.inactivate()

        self.assertFalse(user.is_active)
    
    def test_get_active_user_method(self):
        user = User.register("Muhamad Abdul Muis", "abdulmuis", "password")
        user_from_get_active_method = User.get_active_user(user.id)

        self.assertEqual(user_from_get_active_method, user)
    
    def test_id_not_found_get_active_user_method(self):
        try:
            User.get_active_user(100)
            
            self.assertTrue(False)
        except Exception as error:
            self.assertIsInstance(error, NotFound)
    
    def test_not_found_get_active_user_method(self):
        try:
            user = User.register("Muhamad Abdul Muis", "abdulmuis", "password")
            user.inactivate()

            User.get_active_user(user.id)

            self.assertTrue(False)
        except Exception as error:
            self.assertIsInstance(error, NotFound)


class AuthViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = AuthUserView
        self.url = '/users/auth/'

        self.user = User.register("Test User", "test", "password")
    
    def get_view(self, method):
        return self.view.as_view(method)
    
    def get_response(self, request, view_method: dict):
        view = self.get_view(view_method)
        response = view(request)
        response.render()
        return response
    
    def test_status_code_register_api(self):
        data = {"name": "Abdul Muis", "username": "abdulmuis", "password": "password"}

        request = self.factory.post(f'{self.url}register/', data=data)
        response = self.get_response(request, {'post': 'register'})

        self.assertEqual(response.status_code, 201)

    def test_response_body_register_api(self):
        data = {"name": "Abdul Muis", "username": "abdulmuis", "password": "password"}

        request = self.factory.post(f'{self.url}register/', data=data)
        response = self.get_response(request, {'post': 'register'})
        response_data = json.loads(response.content.decode())

        self.assertEqual(response_data, {"message": "success"})

    def test_status_code_login_api(self):
        data = {"username": "test", "password": "password"}

        request = self.factory.post(f'{self.url}login/', data=data)
        response = self.get_response(request, {'post': 'login'})
        
        self.assertEqual(response.status_code, 200)
    
    def test_response_body_login_api(self):
        data = {"username": "test", "password": "password"}

        request = self.factory.post(f'{self.url}login/', data=data)
        response = self.get_response(request, {'post': 'login'})
        response_data = json.loads(response.content.decode())

        self.assertEqual(response_data["id"], self.user.id)
        self.assertIsNotNone(response_data.get("token"))

    def test_response_body_not_found_user_login_api(self):
        data = {"username": "test", "password": "password1"}

        request = self.factory.post(f'{self.url}login/', data=data)
        response = self.get_response(request, {'post': 'login'})
        response_data = json.loads(response.content.decode())

        self.assertEqual(response_data["detail"].lower(), "not found.")
    
    def test_status_code_not_found_user_login_api(self):
        data = {"username": "test", "password": "password1"}

        request = self.factory.post(f'{self.url}login/', data=data)
        response = self.get_response(request, {'post': 'login'})

        self.assertEqual(response.status_code, 404)
