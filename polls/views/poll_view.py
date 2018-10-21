from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from polls.models.poll_models import Question, Choice
from django.urls import reverse
from django.db.models import F
from datetime import datetime


def index(request):
    # pub_date__lte can not return future publish date
    latest_question_list = Question.objects.filter(pub_date__lte=datetime.now()).order_by("-pub_date")[:5]
    context = dict(
        latest_question_list=latest_question_list,
    )
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    # try:
    #     question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #     raise Http404("页面不存在的哦")
    question = get_object_or_404(Question, pk=question_id, pub_date__lte=datetime.now())
    return render(request, "polls/detail.html", {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id, pub_date__lte=datetime.now())
    return render(request, "polls/results.html", dict(question=question))


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id, pub_date__lte=datetime.now())
    try:
        choice = Choice.objects.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request,
                      "polls/detail.html",
                      dict(
                          question=question,
                          error_message="the choice not exist!"
                      ))
    else:
        # race condition use F
        choice.votes = F('votes') + 1
        choice.save(update_fields=['votes'])
        return HttpResponseRedirect(reverse("polls:results", args=(question_id, )))
