from django.db import models

class User(models.Model):
    email = models.CharField(max_length=200,blank=True)
    password = models.CharField(max_length=200,blank=True)
    api_token = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_authenticated(self):
        return True

    class Meta:
        db_table = 'user'


class Note(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField()
    user = models.ForeignKey(User, related_name="notes", on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'notes'