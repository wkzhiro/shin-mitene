from allauth.account.forms import SignupForm
from django import forms
from .models import CustomUser
from allauth.account.adapter import DefaultAccountAdapter

from wagtail.users.forms import UserEditForm, UserCreationForm

from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        # fields = ['avatar']  # avatarフィールドを含める

class CustomSignupForm(SignupForm):
    # last_name = forms.CharField()
    # first_name = forms.CharField()
    
    class Meta:
        model = CustomUser

    def signup(self, request,user):
        user.last_name = self.cleaned_data['last_name']
        user.first_name = self.cleaned_data['first_name']


        user.save()
        return user
    

# class CustomUserEditForm(UserEditForm):
#     # avatar = forms.ImageField(required=False)

#     class Meta(UserEditForm.Meta):
#         model = CustomUser
#         # UserEditForm.Meta.fields は username, email等が含まれているため
#         # そこにavatarを追加します
#         # fields = list(UserEditForm.Meta.fields) + ['avatar']
#         # fields = tuple(fields)  # 最終的にタプルに戻したい場合

# class CustomUserCreationForm(UserCreationForm):
#     # avatar = forms.ImageField(required=False)

#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         # fields = list(UserEditForm.Meta.fields) + ['avatar']
#         # fields = tuple(fields)  # 最終的にタプルに戻したい場合