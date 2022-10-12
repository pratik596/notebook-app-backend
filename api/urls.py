from .views import *
from django.urls import path

urlpatterns = [
    path('user/signup', SignUp.as_view()),
    path('user/login', LoginUser.as_view()),
    path('user/getuser', GetUser.as_view()),
    path('notes/', NoteList.as_view()),
    path('notes/<int:pk>', NoteDetail.as_view()),
]
