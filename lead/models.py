from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


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
    completed = models.BooleanField(default=False)
    trash = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.title)


class Reminder(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    updateDate = models.DateTimeField(auto_created=True, auto_now=True, blank=False, null=False)
    dueDate = models.DateField(auto_created=True, blank=False, null=False)
    dueTime = models.TimeField(default=timezone.now, blank=False, null=False)
    email = models.BooleanField(default=False)
    trash = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.task.pk})

    def __str__(self):
        return str(self.task)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    image = models.ImageField(blank=True, null=True)
    phonenumber = models.CharField(max_length=30)

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
