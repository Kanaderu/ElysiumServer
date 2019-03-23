from django import forms
from django.utils.translation import ugettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm

from .models import MembershipStatus


class CustomUserEditForm(UserEditForm):
    country = forms.CharField(required=True, label=_("Country"))
    status = forms.ModelChoiceField(queryset=MembershipStatus.objects, required=True, label=_("Status"))

    facebook = forms.CharField(required=False, label=_("Facebook"), help_text='Facebook Username found in https://www.facebook.com/<username>')
    twitter = forms.CharField(required=False, label=_('Twitter'), help_text='Twitter Username, without the @, found in https://twitter.com/<username>')
    instagram = forms.CharField(required=False, label=_('Instagam'), help_text='Instagram Username, without the @, found in https://www.instagram.com/<username>')
    pinterest = forms.CharField(required=False, label=_('Pinterest'), help_text='Pinterest Username found in https://www.pinterest.com/<username>')
    google_plus = forms.CharField(required=False, label=_('Google Plus'), help_text='Google+ Username, without the +, found in https://plus.google.com/+<username>')
    linkedin = forms.CharField(required=False, label=_('LinkedIn'), help_text='LinkedIn Username found in https://linkedin.com/in/<username>')


class CustomUserCreationForm(UserCreationForm):
    country = forms.CharField(required=True, label=_("Country"))
    status = forms.ModelChoiceField(queryset=MembershipStatus.objects, required=True, label=_("Status"))

