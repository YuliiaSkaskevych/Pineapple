from django.urls import path
from . import views
from .views import QuoteCreate, QuoteListView, UserListView, LoanedQuotesByUserListView, QuoteChange, QuoteDelete
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(0)(views.index), name='index'),
    path('users/', UserListView.as_view(), name='users'),
    path('users/<int:id>/', cache_page(2)(views.user_info), name='detail_user'),
    path("create_post/", QuoteCreate.as_view(), name='create_post'),
    path("my_posts/", LoanedQuotesByUserListView.as_view(), name='my_posts'),
    path("my_posts/<int:pk>/", QuoteChange.as_view(), name='change_my_posts'),
    path("my_posts/<int:pk>/delete/", QuoteDelete.as_view(), name='delete_quote'),
    path('posts/', QuoteListView.as_view(), name='posts'),
    path("posts/<int:pk>/", cache_page(2)(views.detail_post), name='detail_post'),
    ]
