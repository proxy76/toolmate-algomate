from django.urls import path

from .views import GenerateView, SessionListCreateView, SimulateView, TopicsView

urlpatterns = [
    path("topics/", TopicsView.as_view(), name="topics"),
    path("generate/", GenerateView.as_view(), name="generate"),
    path("simulate/", SimulateView.as_view(), name="simulate"),
    path("sessions/", SessionListCreateView.as_view(), name="sessions"),
]
