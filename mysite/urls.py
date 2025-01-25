from django.conf import settings
from django.urls import include, path,re_path  
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from mitene.views import LikePostView, UnlikePostView, BookmarkView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path('accounts/', include('allauth.urls')), # Creates urls like yourwebsite.com/login/
    path('like/<int:post_id>/', LikePostView.as_view(), name='like_post'),
    path('unlike/<int:post_id>/', UnlikePostView.as_view(), name='unlike_post'),
    path('bookmark/<int:post_id>/', BookmarkView.as_view(), name='bookmark'),
    path('silk/', include('mysite.silk_secure_urls', namespace='silk')),
]


urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
