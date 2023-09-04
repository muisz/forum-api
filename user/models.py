from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    @property
    def name(self):
        if self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name

    @classmethod
    def register(cls, name: str, username: str, password: str):
        user = cls(username=username)
        user.set_name(name)
        user.set_password(password)
        user.save()
        return user
    
    @classmethod
    def login(cls, username: str, password: str):
        user = cls.objects.filter(username=username, is_active=True).first()
        if user is None or not user.check_password(password):
            raise NotFound()
        
        token = user.generate_token()
        user.last_login = timezone.now()
        user.save()

        user.token = token

        return user
    
    @classmethod
    def get_active_user(cls, id):
        user = cls.objects.filter(id=id, is_active=True).first()
        if user is None:
            raise NotFound(f'user with id of {id} not found')
        return user
    
    def set_name(self, name: str):
        names = name.split(' ')
        first_name = names[0]
        last_name = None
        if len(names) > 1:
            last_name = ' '.join(word for word in names[1:])
        self.first_name = first_name
        self.last_name = last_name

    def generate_token(self):
        token = RefreshToken.for_user(self)
        return {"access": str(token.access_token), "refresh": str(token)}

    def inactivate(self):
        self.is_active = False
        self.save()
