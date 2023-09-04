from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from .models import User
from .serializers import (
    AuthUserSerializer,
    LoginUserSerializer,
    RegisterUserSerializer,
)

class AuthUserView(GenericViewSet):
    permission_classes = ()
    
    @action(methods=['post'], detail=False)
    def register(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.data

        User.register(validated_data["name"], validated_data["username"], validated_data["password"])

        return Response({"message": "success"}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def login(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.data

        user = User.login(validated_data["username"], validated_data["password"])

        response_serializer = AuthUserSerializer(user, context=self.get_serializer_context())
        return Response(response_serializer.data)
