from django.db import models
from datetime import datetime, timedelta


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def was_published_recently(self):
        now = datetime.now()
        return now >= self.pub_date >= now + timedelta(days=-1)

    def __str__(self):
        return self.question_text

    class Meta:
        db_table = "question"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

    class Meta:
        db_table = "choice"
