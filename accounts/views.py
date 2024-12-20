from django.shortcuts import render
from .forms import CustomSignupForm

# Create your views here.
def my_view(request):
    if request.method == 'POST':
        print("FILES:", request.FILES)  # アップロードされたファイルを確認
        form = CustomSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # print("User saved with avatar:", user.avatar)