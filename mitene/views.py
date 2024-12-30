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

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

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

        # context = super().get_context(request)
        # query = request.GET.get('q', None)
        # if query:
        #     # PostPageを検索
        #     search_results = PostPage.objects.live().search(query)
        #     context['search_results'] = search_results
        # return context
        
        # .env をロード
        load_dotenv()

        # Azure AI Searchの設定
        search_endpoint = os.getenv('COG_END_POINT')  
        search_credential = AzureKeyCredential(os.getenv('COG_API_KEY')  )
        index_name =  os.getenv('INDEX_NAME')  
        semantic_config_name = os.getenv('SEMANTIC_CONFIG_NAME')  
        
        context = super().get_context(request)
        search_query = request.GET.get("q", None)
        page_number = int(request.GET.get("page", 1))
        results_per_page = 20

        # Azure AI Searchクライアントの初期化
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=search_credential
        )

        print("search")


        # 検索結果の初期化
        search_results = []
        total_count = 0

        if search_query:
            # Azure AI Searchで検索
            search_response = search_client.search(
                search_text=search_query,
                select=['chunk_id', 'chunk', 'tags', 'parent_filename', 'creation_date'],
                top=results_per_page,
                skip=(page_number - 1) * results_per_page
            )

            # 検索結果をリスト化
            search_results = list(search_response)
            total_count = search_response.get_count()

        # Pagination
        paginator = Paginator(search_results, results_per_page)
        try:
            search_results = paginator.page(page_number)
        except PageNotAnInteger:
            search_results = paginator.page(1)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)

        # コンテキストに検索結果を追加
        context["search_query"] = search_query
        context["search_results"] = search_results
        context["total_count"] = total_count
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
