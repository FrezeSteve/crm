from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse, HttpResponse
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.views.generic import (TemplateView, ListView,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import LeadForm, TaskForm, ReminderForm
from .models import Lead, Task, Reminder
from django.utils import timezone
import matplotlib.pyplot as plt
from django.conf import settings


# Create your views here.
class LeadListView(LoginRequiredMixin, ListView):
    model = Lead

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #  add my own queryset
        if self.request.user.is_authenticated:
            # Task
            context['task_count'] = Task.objects.filter(
                author=self.request.user, trash=False).exclude(
                lead__trash=True).all()
            # pagination
            paginator = Paginator(self.get_queryset(), 12)
            page = self.request.GET.get('page')
            leads = paginator.get_page(page)
            context['lead_list'] = leads
            # reminder
            context['reminders'] = Reminder.objects.filter(
                dueDate__gt=timezone.now(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False  # the reminder is not in the trash
            ).all()
        return context

    def get_queryset(self):
        return Lead.objects.filter(trash=False, assigned=self.request.user).order_by('-pk').all()


class CreateLeadView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'lead/lead_detail.html'
    form_class = LeadForm
    template_name = 'lead/form.html'

    model = Lead

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #  add my own queryset
        if self.request.user.is_authenticated:
            context['task_count'] = Task.objects.filter(author=self.request.user, trash=False).exclude(
                lead__trash=True).all()
            context['create'] = True
            context['reminders'] = Reminder.objects.filter(
                dueDate__gt=timezone.now(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False  # the reminder is not in the trash
            ).all()
        return context


class LeadDetailView(LoginRequiredMixin, DetailView):
    template_name = 'lead/detail.html'
    model = Lead

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #  add my own queryset
        if self.request.user.is_authenticated:
            context['task_count'] = Task.objects.filter(lead=self.object, author=self.request.user, trash=False).all()
            context['task_form'] = TaskForm()
            context['lead_detail'] = True
            context['reminders'] = Reminder.objects.filter(
                dueDate__gt=timezone.now(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False  # the reminder is not in the trash
            ).all()
        return context

    def get_queryset(self):
        return Lead.objects.filter(trash=False).order_by('-pk')


class LeadUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'lead/lead_detail.html'
    template_name = 'lead/form.html'

    form_class = LeadForm

    model = Lead

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #  add my own queryset
        if self.request.user.is_authenticated:
            context['task_count'] = Task.objects.filter(lead=self.object, trash=False).all()
            context['lead_update'] = True
            context['reminders'] = Reminder.objects.filter(
                dueDate__gt=timezone.now(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False  # the reminder is not in the trash
            ).all()
        return context

    def get_queryset(self):
        return Lead.objects.filter(trash=False).order_by('-pk')


# Task
class TaskDetailView(LoginRequiredMixin, DetailView):
    template_name = 'lead/detail.html'
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #  add my own queryset
        if self.request.user.is_authenticated:
            context['task_count'] = Task.objects.filter(
                lead=self.object.lead, author=self.request.user, trash=False).all()
            context['task_detail'] = True
            context['reminder_form'] = ReminderForm()
            context['reminders'] = Reminder.objects.filter(
                dueDate__gt=timezone.now(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False,  # the reminder is not in the trash
                task=self.object
            ).all()
        return context

    def get_queryset(self):
        return Task.objects.filter(trash=False).order_by('-pk')


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'lead/task_detail.html'
    template_name = 'lead/form.html'

    form_class = TaskForm

    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #  add my own queryset
        if self.request.user.is_authenticated:
            context['task_count'] = Task.objects.filter(lead=self.object.lead, trash=False).all()
            context['task_update'] = True
            context['reminders'] = Reminder.objects.filter(
                dueDate__gt=timezone.now(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False,  # the reminder is not in the trash
                task=self.object
            ).all()
        return context

    def get_queryset(self):
        return Task.objects.filter(trash=False).order_by('-pk')


# Reminder


# trashes the lead but doesn't delete it completely from the database
@login_required
def deleteLead(request, pk):
    object = get_object_or_404(Lead, pk=pk)
    if not object.trash:
        object.trash = True
        object.save()
    return HttpResponseRedirect(reverse_lazy('lead_list'))


# trashes the task but doesn't delete it completely from the database
@login_required
def deleteTask(request, pk):
    object = get_object_or_404(Task, pk=pk)
    if not object.trash:
        object.trash = True
        object.save()
    return HttpResponseRedirect(reverse_lazy('lead_list'))


# an endpoint that creates a task
@login_required
def createTask(request, pk):
    if request.user.is_authenticated:
        lead = get_object_or_404(Lead, pk=pk)
        if request.method == "POST":
            form = TaskForm(request.POST)
            print(form.errors)
            if form.is_valid():
                task = form.save(commit=False)
                task.author = request.user
                task.lead = lead
                task.save()
                return HttpResponseRedirect(reverse('lead_detail', kwargs={'pk': pk}))
            else:
                print(form.is_valid())
                return HttpResponseForbidden('<h1>Error!! Not a valid form</h1>')
    else:
        return HttpResponseRedirect(reverse_lazy('login'))
    return HttpResponseForbidden("<h1>I Don't know whats happening</h1>")


# an endpoint that creates a reminder
@login_required
def createReminder(request, pk):
    if request.user.is_authenticated:
        task = get_object_or_404(Task, pk=pk)
        if request.method == "POST":
            form = ReminderForm(request.POST)
            print(form.errors)
            if form.is_valid():
                reminder = form.save(commit=False)
                reminder.task = task
                reminder.save()
                return HttpResponseRedirect(reverse('task_detail', kwargs={'pk': pk}))
            else:
                return HttpResponseForbidden('<h1>Error!! Not a valid form</h1>')
    else:
        return HttpResponseRedirect(reverse_lazy('login'))
    return HttpResponseForbidden("<h1>I Don't know whats happening</h1>")


# Reports Source
@login_required
def reports(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("<h1 class='text-center'>Must be authorized!!!Contact admin</h1>")
    import numpy as np
    x = np.arange(2)
    money = [5, 2]
    plt.bar(x, money)
    plt.xticks(x, ('Facebook', 'Google'))
    import os
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'books_read.png'))
    import csv
    with open(os.path.join(settings.MEDIA_ROOT, 'lead.csv'), mode='w') as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=',', lineterminator='\n', )

        # employee_writer.writerow(['Leads by: {}'.format(request.user.username)])
        employee_writer.writerow(['#', 'Name', 'Location', 'Phone Number', 'Email', 'Description'])
        qs = Lead.objects.filter(trash=False, assigned=request.user).order_by('-pk').all()
        for index, lead in enumerate(qs):
            employee_writer.writerow(
                [
                    '{}'.format(index+1),
                    '{}'.format(lead.name),
                    '{}'.format(lead.location),
                    '{}'.format(lead.phonenumber),
                    '{}'.format(lead.email),
                    '{}'.format(lead.description)]
            )
    context = {
        'image': '/media/books_read.png/',
        'csv': '/media/lead.csv'
    }
    return render(request, 'lead/report.html', context=context)

# Malizia the create reminder
