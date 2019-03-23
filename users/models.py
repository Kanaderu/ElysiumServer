from django.db import models
from django.contrib.auth.models import AbstractUser

from wagtail.snippets.models import register_snippet


class User(AbstractUser):
    country = models.CharField(verbose_name='country', max_length=255)
    status = models.ForeignKey('MembershipStatus', on_delete=models.CASCADE, null=True)
    facebook = models.CharField(max_length=255, help_text='Facebook Username found in https://www.facebook.com/<username>', blank=True, null=True)
    twitter = models.CharField(max_length=255, help_text='Twitter Username, without the @, found in https://twitter.com/<username>', blank=True, null=True)
    instagram = models.CharField(max_length=255, help_text='Instagram Username, without the @, found in https://www.instagram.com/<username>', blank=True, null=True)
    pinterest = models.CharField(max_length=255, help_text='Pinterest Username found in https://www.pinterest.com/<username>', blank=True, null=True)
    google_plus = models.CharField(max_length=255, help_text='Google+ Username, without the +, found in https://plus.google.com/+<username>', blank=True, null=True)
    linkedin = models.CharField(max_length=255, help_text='LinkedIn Username found in https://linkedin.com/in/<username>', blank=True, null=True)


@register_snippet
class MembershipStatus(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Membership Status'