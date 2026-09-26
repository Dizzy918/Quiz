from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with a unique email address."""

    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    KNIGHT_1 = "knight-1"
    KNIGHT_2 = "knight-2"
    KNIGHT_3 = "knight-3"
    KNIGHT_4 = "knight-4"

    AVATAR_CHOICES = [
        (KNIGHT_1, "Knight 1"),
        (KNIGHT_2, "Knight 2"),
        (KNIGHT_3, "Knight 3"),
        (KNIGHT_4, "Knight 4"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    nickname = models.CharField(max_length=30, unique=True)
    avatar_key = models.CharField(
        max_length=30,
        choices=AVATAR_CHOICES,
        default=KNIGHT_1,
    )

    def __str__(self):
        return self.nickname
