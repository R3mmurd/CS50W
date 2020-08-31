from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT


class User(AbstractUser):
    following = models.ManyToManyField(
        RECURSIVE_RELATIONSHIP_CONSTANT,
        symmetrical=False,
        related_name='followers',
        related_query_name='followers'
    )

    def serialize(self):
        return {
            'username': self.username,
            'followers': self.followers.count(),
            'following': self.following.count(),
            'posts': self.posts.count()
        }


class Post(models.Model):
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        related_query_name='posts'
    )
    liked_by = models.ManyToManyField(
        User,
        related_name='liked_posts',
        related_query_name='liked_posts'
    )

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "text": self.text,
            "timestamp": self.timestamp.strftime("%b %-d %Y, %-I:%M %p"),
            "likes": self.liked_by.count()
        }
