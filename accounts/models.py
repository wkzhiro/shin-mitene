from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """拡張ユーザーモデル"""
    class Meta(AbstractUser.Meta):
        db_table = 'custom_user'

    first_name = models.CharField('性', blank=False,max_length=30)
    last_name = models.CharField('名前',blank=False,max_length=30)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def save(self, *args, **kwargs):
        print(f"Save method called")
        # print(f"Avatar value: {self.avatar}")
        # if self.avatar:
            # print(f"Saving avatar to: {self.avatar.path}")
        super().save(*args, **kwargs)