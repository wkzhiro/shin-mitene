from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import PostPage, PostLike,PostBookmark
from django.views.generic.detail import DetailView
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.contrib import messages


from wagtail.models import Page

class LikePostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(PostPage, id=post_id)
        PostLike.objects.get_or_create(user=request.user, post=post)
        return redirect(post.url)

class UnlikePostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(PostPage, id=post_id)
        PostLike.objects.filter(user=request.user, post=post).delete()
        return redirect(post.url)
    
def top_liked_users(request):
    User = get_user_model()
    top_users = User.objects.annotate(like_count=Count('post_likes')).order_by('-like_count')[:10]
    context = {
        'top_users': top_users,
    }
    return render(request, 'top_users.html', context)

class SearchView(Page):
    def get_context(self, request):
        context = super().get_context(request)
        query = request.GET.get('q', None)
        if query:
            # PostPageを検索
            search_results = PostPage.objects.live().search(query)
            context['search_results'] = search_results
        return context
    
class BookmarkView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(PostPage, id=post_id)
        # すでにブックマークしている場合は削除
        bookmark = PostBookmark.objects.filter(user=request.user, post=post)
        if bookmark.exists():
            bookmark.delete()
            messages.success(request, "Post bookmark removed.")
        else:
            # 新たにブックマークを追加
            PostBookmark.objects.create(user=request.user, post=post)
            messages.success(request, "Post bookmarked successfully!")
        return redirect(post.url)
