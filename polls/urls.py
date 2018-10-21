from .views import poll_view
from django.urls import path

app_name = "polls"
urlpatterns = [
    path("", poll_view.index, name="index"),
    path("<int:question_id>/", poll_view.detail, name="detail"),
    path("<int:question_id>/results/", poll_view.results, name="results"),
    path("<int:question_id>/vote/", poll_view.vote, name="vote"),
]
