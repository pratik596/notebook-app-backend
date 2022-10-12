import bcrypt, jwt, random, string
from .serializers import NoteSerializer, SignUpSerializer, UserSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.response import Response
from django.conf import settings
from .models import Note, User
from rest_framework.permissions import IsAuthenticated
from .authentication import MyOwnTokenAuthentication
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import status

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class SignUp(GenericAPIView):
    serializer_class = SignUpSerializer
    
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({"success":False,"message":serializer.errors})

        email = serializer.validated_data.get('email').lower()
        password = serializer.validated_data.get('password')

        if User.objects.filter(email__iexact=email).first():
            return Response({"success":False,"message":"User email already exists"})

        enc_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")

        letters = string.ascii_letters
        random_string = ''.join(random.choice(letters) for i in range(15))
        encoded_token = jwt.encode({ 'email' : email, 'random_string' : random_string }, settings.SECRET_KEY , algorithm='HS256')

        user = User.objects.create(
            email = email,
            password = enc_password,
            api_token = encoded_token
        )
        
        return Response({"success":True,"access_token":encoded_token})


class LoginUser(GenericAPIView):
    
    def post(self, request, *args, **kwargs):

        type = request.data.get('type')
        serializer = SignUpSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error":True,"message":serializer.errors})

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = User.objects.filter(email=email).first()

        if user:
            checkpw = bcrypt.checkpw(password.encode(),user.password.encode())
            if checkpw:
                letters = string.ascii_letters
                random_string = ''.join(random.choice(letters) for i in range(15))
                encoded_token = jwt.encode({ 'email' : user.email, 'random_string' : random_string }, settings.SECRET_KEY , algorithm='HS256')
                user.api_token = encoded_token
                user.save()

                return Response({"success":True,"auth_token":encoded_token})

        return Response({"success":False,"message":"Unauthenticated user"})



class GetUser(GenericAPIView):
    serializer_class = UserSerializer
    authentication_classes = [MyOwnTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class NoteList(ListCreateAPIView):
    serializer_class = NoteSerializer
    authentication_classes = [MyOwnTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Note.objects.filter(user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error":True,"message":serializer.errors})
        d = serializer.save(user=user)
        return Response(serializer.data)


class NoteDetail(RetrieveUpdateDestroyAPIView):
    authentication_classes = [MyOwnTokenAuthentication]
    permission_classes = [IsAuthenticated,IsOwner]
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.perform_destroy(instance)
        return Response({"details":"Deleted"})
