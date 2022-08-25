from django.urls import path
from . import views
from .views import QuoteCreate, QuoteListView, UserListView, LoanedQuotesByUserListView, QuoteChange

urlpatterns = [
    path('', views.index, name='index'),
    path('users/', UserListView.as_view(), name='users'),
    path('users/<int:id>/', views.user_info, name='detail_user'),
    path("create_post/", QuoteCreate.as_view(), name='create_post'),
    path("my_posts/", LoanedQuotesByUserListView.as_view(), name='my_posts'),
    path("my_posts/<int:pk>/", QuoteChange.as_view(), name='change_my_posts'),
    path('posts/', QuoteListView.as_view(), name='posts'),
    path("posts/<int:pk>/", views.detail_post, name='detail_post'),
    path('contact/', views.contact, name="contact"),
    ]
