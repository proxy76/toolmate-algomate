from django.urls import path

from .views import AdminPostListCreateView, PostDetailView, PostListView

urlpatterns = [
    path("posts/", PostListView.as_view(), name="post-list"),
    path("admin/posts/", AdminPostListCreateView.as_view(), name="admin-post-list-create"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
]
