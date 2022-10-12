from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework import serializers
from .models import User, Note

class SignUpSerializer(Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']

class NoteSerializer(ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'title', 'text')
