from django.db import models
from django.contrib.auth.models import AbstractUser

from wagtail.snippets.models import register_snippet


class User(AbstractUser):
    country = models.CharField(verbose_name='country', max_length=255)
    status = models.ForeignKey('MembershipStatus', on_delete=models.CASCADE, null=True)


@register_snippet
class MembershipStatus(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Membership Status'