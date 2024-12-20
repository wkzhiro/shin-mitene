from django.db import models,IntegrityError
from django.db.models import Count

from django import forms  # ここでformsモジュールをインポートします
from django.contrib.auth import get_user_model
from django.contrib import admin

from django.utils import timezone

# Add these:
from wagtail.models import Page, Orderable
from modelcluster.fields import ParentalKey
from wagtail.blocks import TextBlock

from modelcluster.fields import ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag as TaggitTag

from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtailcodeblock.blocks import CodeBlock
from wagtail.blocks import TextBlock, RichTextBlock

from wagtail.snippets.models import register_snippet

# add this:
from wagtail.search import index

class TopPage(Page):

    intro = models.CharField(max_length=255)
    main_body = RichTextField(blank=True)

    side_title = models.CharField(blank=True, max_length=255)
    side_body = RichTextField(blank=True)
    footer_text = models.CharField(blank=True, max_length=255)


    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('main_body', classname="full"),
        FieldPanel('side_title'),
        FieldPanel('side_body', classname="full"),
        FieldPanel('footer_text'),
        InlinePanel('nav_items', label="Nav items"),
    ]

    def get_top_page(self):
        return self
    
    def get_context(self, request):
        context = super().get_context(request)
        context['top_page'] = self.get_top_page()
        return context

class NavItems(Orderable):
    top_page = ParentalKey(TopPage, related_name='nav_items')
    label = models.CharField(max_length=255)
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='+'
    )
    #Orderableクラスの場合はpanels
    panels = [
        FieldPanel('label'),
        FieldPanel('page'),  # chooser_field_nameを追加
    ]

class ListPage(Page):
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    intro = models.CharField(max_length=255)
    main_body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('cover_image'),
        FieldPanel('intro'),
        FieldPanel('main_body', classname="full"),
        InlinePanel('related_pages', label="Related Pages"),
    ]

    parent_page_types = ['mitene.TopPage', 'mitene.ListPage']

    def get_top_page(self):
        pages = self.get_ancestors().type(TopPage)
        return pages[0]
    
    def get_breads(self):
        breads = self.get_ancestors().descendant_of(self.get_top_page(), True)
        return breads

    def get_like_count(self):
            return self.likes.count()

    def get_view_count(self, start_date=None, end_date=None):
        views = self.page_views.all()
        if start_date:
            views = views.filter(viewed_at__gte=start_date)
        if end_date:
            views = views.filter(viewed_at__lte=end_date)
        return views.count()

    def get_context(self, request):
        context = super().get_context(request)
        context['top_page'] = self.get_top_page()
        context['breads'] = self.get_breads()
        User = get_user_model()
        top_users = User.objects.annotate(like_count=Count('post_likes')).order_by('-like_count')[:10]
        context['top_users'] = top_users

        # カテゴリ一覧を取得
        categories = PostCategory.objects.all()
        context['categories'] = categories

        # 並び替え順を取得
        sort_order = request.GET.get('sort', 'updated')
        context['sort_order'] = sort_order  # テンプレートで現在の並び順を表示するため

        # 検索クエリの処理
        search_query = request.GET.get('q', None)
        if search_query:
            # 検索結果を取得
            page_list = PostPage.objects.live().search(search_query)
        else:
            # 通常のページリスト
            if self.related_pages.count():
                page_list = [item.page.specific for item in self.related_pages.all()]
            else:
                tag = request.GET.get('tag')
                category = request.GET.get('category')
                if category:
                    context['category'] = category
                    page_list = PostPage.objects.descendant_of(self.get_top_page()).filter(categories__name=category).live().order_by('-first_published_at')
                elif tag:
                    context['tag'] = tag
                    page_list = PostPage.objects.descendant_of(self.get_top_page()).filter(tags__name=tag).live().order_by('-first_published_at')
                else:
                    page_list = self.get_children().live().specific().order_by('-first_published_at')

        # 各ページにいいね数と閲覧数を追加
        for page in page_list:
            specific_page = page.specific
            specific_page.like_count = specific_page.get_like_count() if hasattr(specific_page, 'get_like_count') else 0
            specific_page.total_views = specific_page.get_view_count() if hasattr(specific_page, 'get_view_count') else 0

        # 並び替えの適用
        if sort_order == 'views':
            page_list = sorted(page_list, key=lambda x: x.specific.total_views, reverse=True)
        elif sort_order == 'likes':
            page_list = sorted(page_list, key=lambda x: x.specific.like_count, reverse=True)
        elif sort_order == 'updated':
            page_list = sorted(page_list, key=lambda x: x.last_published_at, reverse=True)

        context['page_list'] = page_list
        if search_query:
            context['search_query'] = search_query  # 検索クエリをテンプレートに渡す

        return context
    

class RelatedPages(Orderable):
    base_page = ParentalKey(Page, related_name='related_pages')
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='+'
    )
    panels = [
        FieldPanel('page'),
    ]

class PostPage(Page):
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    intro = models.CharField(max_length=250)
    main_body = StreamField([
        ('rich_text', RichTextBlock(icon='doc-full', label='Rich Text')),
        ('code', CodeBlock(icon='code', label='Pretty Code')),
    ], null=True, blank=True, use_json_field=True)

    categories = ParentalManyToManyField(
        'mitene.PostCategory',
        blank=True
        )
    tags = ClusterTaggableManager(
        through='mitene.PostTag',
        blank=True
        )

    content_panels = Page.content_panels + [
        FieldPanel('cover_image'),
        FieldPanel('intro'),
        FieldPanel('main_body'),
        InlinePanel('related_pages', label="Related Pages"),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('tags'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),       # タイトルを検索対象にする
        index.SearchField('intro'),       # 本文のイントロ部分を検索対象にする
        index.SearchField('main_body')    # 本文全体を検索対象にする
    ]

    parent_page_types = ['mitene.ListPage']
    subpage_types = []

    def get_top_page(self):
        pages = self.get_ancestors().type(TopPage)
        return pages[0]
    
    def get_breads(self):
        breads = self.get_ancestors().descendant_of(self.get_top_page(), True)
        return breads

    def get_like_count(self):
        return self.likes.count()

    def is_liked_by_user(self, user):
        return self.likes.filter(user=user).exists()

    def serve(self, request):
        response = super().serve(request)
        if request.user.is_authenticated:
            try:
                PageView.objects.create(user=request.user, page=self)
            except IntegrityError:
                # ユニーク制約により、同日に同じユーザーの重複カウントを防止
                pass
        return response

    def get_view_count(self, start_date=None, end_date=None):
        views = self.page_views.all()
        if start_date:
            views = views.filter(viewed_at__gte=start_date)
        if end_date:
            views = views.filter(viewed_at__lte=end_date)
        return views.count()

    def get_context(self, request):
        context = super().get_context(request)
        context['top_page'] = self.get_top_page()
        context['breads'] = self.get_breads()
        context['like_count'] = self.get_like_count()
        context['has_liked'] = self.is_liked_by_user(request.user) if request.user.is_authenticated else False
        User = get_user_model()
        top_users = User.objects.annotate(like_count=Count('post_likes')).order_by('-like_count')[:10]
        context['top_users'] = top_users
        context['total_views'] = self.get_view_count()
        # 例えば過去7日間のビュー数
        start_date = timezone.now().date() - timezone.timedelta(days=30)
        context['monthly_views'] = self.get_view_count(start_date=start_date)
        context['has_bookmarked'] = self.bookmarks.filter(user=request.user).exists() if request.user.is_authenticated else False

        return context

User = get_user_model()

class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey('mitene.PostPage', on_delete=models.CASCADE, related_name='likes')
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = "Like"  # 管理画面に表示される名前
        verbose_name_plural = "Likes"  # 複数形の場合の名前

    def __str__(self):
        return f"{self.user} likes {self.post}"

class PageView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_views')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='page_views')
    viewed_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'page', 'viewed_at')

    def __str__(self):
        return f"{self.user} viewed {self.page} on {self.viewed_at}"

class PostBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_bookmarks')
    post = models.ForeignKey('mitene.PostPage', on_delete=models.CASCADE, related_name='bookmarks')
    bookmarked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"

    def __str__(self):
        return f"{self.user} bookmarked {self.post}"

@register_snippet
class PostCategory(models.Model):
    name = models.CharField(max_length=255)
    panels = [
        FieldPanel('name'),
    ]
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class PostTag(TaggedItemBase):
    content_object = ParentalKey(PostPage, related_name='tagged_posts')

@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'liked_at')
    list_filter = ('liked_at',)
    search_fields = ('user__username', 'post__title')

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'page', 'viewed_at')
    list_filter = ('viewed_at', 'page')
    search_fields = ('user__username', 'page__title')

@admin.register(PostBookmark)
class PostBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'bookmarked_at')
    list_filter = ('bookmarked_at', 'user', 'post')
    search_fields = ('user__username', 'post__title')

@register_snippet
class PostBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_bookmarks')
    post = models.ForeignKey('mitene.PostPage', on_delete=models.CASCADE, related_name='bookmarks')
    bookmarked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"

    def __str__(self):
        return f"{self.post}"
