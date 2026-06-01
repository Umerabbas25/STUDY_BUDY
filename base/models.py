from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Topics(models.Model):
    name =  models.CharField(max_length=200)
    updated  =  models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Room(models.Model):
    host = models.ForeignKey(User,on_delete=models.CASCADE)
    topic =  models.ForeignKey(Topics,on_delete=models.SET_NULL, null=True)
    name =  models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    updated  =  models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField(max_length=500)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.body[:50]


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class TopicFollow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topic_follows')
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE, related_name='followers')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user.username} follows {self.topic.name}"