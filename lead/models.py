from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import datetime


# Create your models here.
class Status(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class Source(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class Lead(models.Model):
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    assigned = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    phonenumber = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    trash = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('lead_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.name)


class Task(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    description = models.TextField()
    active = models.BooleanField(default=True)
    trash = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)


class Reminder(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    updateDate = models.DateTimeField(auto_created=True, auto_now=True, blank=False, null=False)
    dueDate = models.DateField(auto_created=True, blank=False, null=False)
    dueTime = models.TimeField(default=timezone.now, blank=False, null=False)
    email = models.BooleanField(default=False)
    trash = models.BooleanField(default=False)

    def __str__(self):
        return str(self.task)
