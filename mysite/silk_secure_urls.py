# mysite/silk_secure_urls.py

from django.urls import path
from django.contrib.auth.decorators import login_required

# Silkの各ビューをインポート
from silk.views.clear_db import ClearDBView
from silk.views.cprofile import CProfileView
from silk.views.profile_detail import ProfilingDetailView
from silk.views.profile_dot import ProfileDotView
from silk.views.profile_download import ProfileDownloadView
from silk.views.profiling import ProfilingView
from silk.views.raw import Raw
from silk.views.request_detail import RequestView
from silk.views.requests import RequestsView
from silk.views.sql import SQLView
from silk.views.sql_detail import SQLDetailView
from silk.views.summary import SummaryView

app_name = 'silk'

urlpatterns = [
    path('', login_required(SummaryView.as_view()), name='summary'),
    path('requests/', login_required(RequestsView.as_view()), name='requests'),
    path(
        'request/<uuid:request_id>/',
        login_required(RequestView.as_view()),
        name='request_detail'
    ),
    path(
        'request/<uuid:request_id>/sql/',
        login_required(SQLView.as_view()),
        name='request_sql'
    ),
    path(
        'request/<uuid:request_id>/sql/<int:sql_id>/',
        login_required(SQLDetailView.as_view()),
        name='request_sql_detail'
    ),
    path(
        'request/<uuid:request_id>/raw/',
        login_required(Raw.as_view()),
        name='raw'
    ),
    path(
        'request/<uuid:request_id>/pyprofile/',
        login_required(ProfileDownloadView.as_view()),
        name='request_profile_download'
    ),
    path(
        'request/<uuid:request_id>/json/',
        login_required(ProfileDotView.as_view()),
        name='request_profile_dot'
    ),
    path(
        'request/<uuid:request_id>/profiling/',
        login_required(ProfilingView.as_view()),
        name='request_profiling'
    ),
    path(
        'request/<uuid:request_id>/profile/<int:profile_id>/',
        login_required(ProfilingDetailView.as_view()),
        name='request_profile_detail'
    ),
    path(
        'request/<uuid:request_id>/profile/<int:profile_id>/sql/',
        login_required(SQLView.as_view()),
        name='request_and_profile_sql'
    ),
    path(
        'request/<uuid:request_id>/profile/<int:profile_id>/sql/<int:sql_id>/',
        login_required(SQLDetailView.as_view()),
        name='request_and_profile_sql_detail'
    ),
    path(
        'profile/<int:profile_id>/',
        login_required(ProfilingDetailView.as_view()),
        name='profile_detail'
    ),
    path(
        'profile/<int:profile_id>/sql/',
        login_required(SQLView.as_view()),
        name='profile_sql'
    ),
    path(
        'profile/<int:profile_id>/sql/<int:sql_id>/',
        login_required(SQLDetailView.as_view()),
        name='profile_sql_detail'
    ),
    path('profiling/', login_required(ProfilingView.as_view()), name='profiling'),
    path('cleardb/', login_required(ClearDBView.as_view()), name='cleardb'),
    path(
        'request/<uuid:request_id>/cprofile/',
        login_required(CProfileView.as_view()),
        name='cprofile'
    ),
]
