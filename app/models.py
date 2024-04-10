from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    avatar = models.ImageField(default='img.jpg', upload_to='img')
    bio = models.TextField()

    def __str__(self):
        return self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def hot_questions(self):
        return self.order_by('-rating', 'created_at')

    def last_questions(self):
        return self.order_by('-created_at')


class Question(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    objects = QuestionManager()

    def update_rating(self):
        self.rating = 0
        for like in self.questionlike_set.all():
            if like.is_liked:
                self.rating += 1
            else:
                self.rating -= 1
        self.save()
        return self.rating

    def __str__(self):
        return self.title


class AnswerManager(models.Manager):
    def hot_answer(self):
        return self.order_by('-rating', '-created_at')


class Answer(models.Model):
    text = models.TextField()
    rating = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AnswerManager()

    def update_rating(self):
        self.rating = 0
        for like in self.answerlike_set.all():
            if like.is_liked:
                self.rating += 1
            else:
                self.rating -= 1
        self.save()
        return self.rating


class QuestionLikeManager(models.Manager):
    def like(self, user, question, is_liked):
        like = self.get_or_create(user=user, question=question)
        like.is_liked = is_liked
        like.save()
        return question.update_rating()


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=True)
    objects = QuestionLikeManager()


class AnswerLikeManager(models.Manager):
    def like(self, user, answer, is_liked):
        like = self.get_or_create(user=user, answer=answer)
        like.is_liked = is_liked
        like.save()
        return answer.update_rating()


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=True)
    objects = AnswerLikeManager()


