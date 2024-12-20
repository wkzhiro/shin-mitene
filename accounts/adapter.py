from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import Group
import logging

logger = logging.getLogger(__name__)


class AccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        user = super(AccountAdapter, self).save_user(request, user, form, commit=False)
        # print("Avatar in cleaned_data:", form.cleaned_data.get('avatar'))  # 確認用
        user.last_name = form.cleaned_data.get('last_name')
        user.first_name = form.cleaned_data.get('first_name')
        # user.avatar = form.cleaned_data.get('avatar')  # avatarを保存

        if commit:
            user.save()

        return user