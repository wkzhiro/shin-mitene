# wagtail_hooks.py
from wagtail.admin.views.account import BaseSettingsPanel
from wagtail import hooks
# from .forms import CustomSettingsForm

# @hooks.register('register_account_settings_panel')
# class CustomSettingsPanel(BaseSettingsPanel):
#     name = 'custom'
#     title = "プロフィール画像"
#     order = 500
#     form_class = CustomSettingsForm
#     form_object = 'user'  # userモデルを対象