from django import forms
from django.utils.translation import ugettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm

from .models import MembershipStatus


class CustomUserEditForm(UserEditForm):
    country = forms.CharField(required=True, label=_("Country"))
    status = forms.ModelChoiceField(queryset=MembershipStatus.objects, required=True, label=_("Status"))


class CustomUserCreationForm(UserCreationForm):
    country = forms.CharField(required=True, label=_("Country"))
    status = forms.ModelChoiceField(queryset=MembershipStatus.objects, required=True, label=_("Status"))

