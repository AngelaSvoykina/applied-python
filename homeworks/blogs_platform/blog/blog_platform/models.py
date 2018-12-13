from django.conf import settings
from django.db import models
from django.utils import timezone

class Post(models.Model):
    # author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title =     models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    is_hidden = models.BooleanField(default=False)


    def __str__(self):
        return self.title

    def publish(self):
        self.published_date = timezone.now()
        self.save()



class Comment(models.Model):
    # author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.text

    def publish(self):
        self.published_date = timezone.now()
        self.save()