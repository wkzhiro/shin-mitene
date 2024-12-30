from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

import os
from dotenv import load_dotenv

from wagtail.models import Page

# To enable logging of search queries for use with the "Promoted search results" module
# <https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html>
# uncomment the following line and the lines indicated in the search function
# (after adding wagtail.contrib.search_promotions to INSTALLED_APPS):

# from wagtail.contrib.search_promotions.models import Query


# def search(request):
    # print("search start")
    # search_query = request.GET.get("query", None)
    # page = request.GET.get("page", 1)

    # # Search
    # if search_query:
    #     search_results = Page.objects.live().search(search_query)

    #     # To log this query for use with the "Promoted search results" module:

    #     # query = Query.get(search_query)
    #     # query.add_hit()

    # else:
    #     search_results = Page.objects.none()

    # # Pagination
    # paginator = Paginator(search_results, 10)
    # try:
    #     search_results = paginator.page(page)
    # except PageNotAnInteger:
    #     search_results = paginator.page(1)
    # except EmptyPage:
    #     search_results = paginator.page(paginator.num_pages)

    # return TemplateResponse(
    #     request,
    #     "search/search.html",
    #     {
    #         "search_query": search_query,
    #         "search_results": search_results,
    #     },
    # )


# .env をロード
load_dotenv()

# Azure AI Searchの設定
search_endpoint = os.getenv('COG_END_POINT')  
search_credential = AzureKeyCredential(os.getenv('COG_API_KEY')  )
index_name =  os.getenv('INDEX_NAME')  
semantic_config_name = os.getenv('SEMANTIC_CONFIG_NAME')  


def search(request):

    print("search")
    search_query = request.GET.get("query", None)
    page = int(request.GET.get("page", 1))
    results_per_page = 20

    # Azure AI Searchクライアントの初期化
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=index_name,
        credential=search_credential
    )
    # 検索結果の初期化
    search_results = []
    total_count = 0

    if search_query:
        # Azure AI Searchで検索
        search_response = search_client.search(
            search_text=search_query,
            select=['chunk_id', 'chunk', 'tags','parent_filename','creation_date'],  # 必要なフィールドを指定
            top=results_per_page,
            skip=(page - 1) * results_per_page
        )
        
        # 検索結果をリスト化
        search_results = list(search_response)
        total_count = search_response.get_count()

    print("results",search_results, "total_count",total_count)

    # Pagination
    paginator = Paginator(search_results, results_per_page)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
            "total_count": total_count,
        },
    )
