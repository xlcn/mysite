from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse

from polls.models.poll_models import Question


def create_question(question_text, days):
    pub_date = datetime.now() + timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=pub_date)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        future_time = datetime.now() + timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        old_time = datetime.now() + timedelta(days=-1, seconds=-1)
        old_question = Question(pub_date=old_time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recently_question(self):
        recently_time = datetime.now() - timedelta(hours=23, minutes=59, seconds=59)
        recently_question = Question(pub_date=recently_time)
        self.assertIs(recently_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available!")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        create_question("Past question.", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_future_question(self):
        create_question("Future question.", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available!")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_question(self):
        create_question("Future question.", 30)
        create_question("Past question.", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_two_past_questions(self):
        create_question("Past question 1.", -5)
        create_question("Past question 2.", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question 1.>', '<Question: Past question 2.>'])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question("Future question.", days=30)
        url = reverse("polls:detail", args=(future_question.id, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question("Past question.", days=-3)
        response = self.client.get(reverse("polls:detail", args=(past_question.id,)))
        self.assertContains(response, past_question.question_text)
