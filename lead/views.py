from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView)
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, reverse, redirect
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import LeadForm, TaskForm, ReminderForm, UserChangeForm, UserEditForm
from .models import Lead, Task, Reminder, Source, Status

from threading import Timer
import matplotlib.pyplot as plt
import numpy as np
import csv
import os


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
                task__completed=False,
                dueDate__gte=timezone.now().today(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False  # the reminder is not in the trash
            ).all()
            # datagenTasks()
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
                task__completed=False,
                dueDate__gte=timezone.now().today(),  # make sure that the dueDate has not expired
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
                task__completed=False,
                dueDate__gte=timezone.now().today(),  # make sure that the dueDate has not expired
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
                task__completed=False,
                dueDate__gte=timezone.now().today(),  # make sure that the dueDate has not expired
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
            context['reminders'] = Reminder.objects.filter(
                task__completed=False,
                dueDate__gte=timezone.now().today(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False,  # the reminder is not in the trash
                task=self.object
            ).all()
            context['reminder_form'] = ReminderForm()
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
                task__completed=False,
                dueDate__gte=timezone.now().today(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False,  # the reminder is not in the trash
                task=self.object
            ).all()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.completed:
            return HttpResponseForbidden("<h1 style='color:red;text-align:center;'>Cant change this task!</h1>")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Task.objects.filter(trash=False).order_by('-pk')


# Reminder
class ReminderUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'lead/task_detail.html'
    template_name = 'lead/form.html'

    form_class = ReminderForm

    model = Reminder

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #  add my own querysets
        if self.request.user.is_authenticated:
            context['task_count'] = Task.objects.filter(lead=self.object.task.lead, trash=False).all()
            context['reminder_update'] = True
            context['reminders'] = Reminder.objects.filter(
                task__completed=False,
                dueDate__gte=timezone.now().today(),  # make sure that the dueDate has not expired
                task__author=self.request.user,  # the user is the one is the owner
                trash=False,  # the reminder is not in the trash
                task=self.object.task
            ).all()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.task.completed:
            return HttpResponseForbidden("<h1 style='color:red;text-align:center;'>Cant change this Reminder!</h1>")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Reminder.objects.filter(task__trash=False).order_by('-pk')


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
    # if the task is completed you can't delete it
    if object.completed:
        return HttpResponseForbidden("<h1 style='color:red;text-align:center;'>Cant delete this task!</h1>")
    if not object.trash:
        object.trash = True
        object.save()
    return HttpResponseRedirect(reverse_lazy('lead_list'))


# trashes the reminder but doesn't delete it completely from the database
@login_required
def deleteReminder(request, pk):
    object = get_object_or_404(Reminder, pk=pk)
    pk = object.task.pk
    # if the reminder is completed you can't delete it
    if object.task.completed:
        return HttpResponseForbidden("<h1 style='color:red;text-align:center;'>Cant delete this reminder!</h1>")
    if not object.trash:
        object.trash = True
        object.save()
    return HttpResponseRedirect(reverse_lazy('task_detail', kwargs={'pk': pk}))


# the task is completed
@login_required
def completeTask(request, pk):
    object = get_object_or_404(Task, pk=pk)
    # if the task is completed you can't update it
    if object.completed:
        return HttpResponseForbidden("<h1 style='color:red;text-align:center;'>Cant complete it twice!</h1>")
    if not object.completed:
        object.completed = True
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


# Reminder
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


# User Profile
@login_required
def userProfile(request):
    form1 = UserEditForm()
    if request.method == 'POST':
        form = UserChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserChangeForm(request.user)
        form1 = UserEditForm()
    return render(request, 'lead/user_profile.html', {'user': request.user, "form": form, 'form1': form1})


# EndPoint for editing User Profile
@login_required
def changerProfile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES)
        if form.is_valid():
            # save the various fields into their respective models
            object = get_object_or_404(User, id=request.user.id)
            image = form.cleaned_data['image']
            email = form.cleaned_data['email']
            phoneN = form.cleaned_data['phonenumber']
            if image is not None:
                object.profile.image = image
            elif email is not None:
                object.email = email
            elif phoneN is not None:
                object.profile.phonenumber = phoneN
            object.save()
            messages.success(request, 'Your have successfully edited your profile!')
            return redirect('password_change')
    return HttpResponseForbidden("<h1>I Don't know whats happening</h1>")


# EndPoint for changing status to customer
@login_required
def statusComplete(request, pk):
    object = get_object_or_404(Lead, pk=pk)
    pk = object.task.pk
    # if the reminder is completed you can't delete it
    if object.task.completed:
        return HttpResponseForbidden("<h1 style='color:red;text-align:center;'>Cant delete this reminder!</h1>")
    if not object.trash:
        object.trash = True
        object.save()
    return HttpResponseRedirect(reverse_lazy('task_detail', kwargs={'pk': pk}))
    pass

# Reports Source
@login_required
def reports(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("<h1 class='text-center'>Must be authorized!!!Contact admin</h1>")
    # get the number of sources registered in the application
    sources = Status.objects.all()
    x = np.arange(len(sources))
    # get the number of leads that were converted using the various sources available
    leads = Lead.objects.all()
    source_name = []
    count = []
    for source in sources:
        source_name.append(source.name)
        count.append(leads.filter(status=source).count())
    plt.bar(x, count)
    plt.xticks(x, source_name)

    report_name = 'stauts' + '_{}.png'.format(request.user.username)

    plt.savefig(os.path.join(settings.MEDIA_ROOT, report_name))
    plt.close()
    # get the number of sources registered in the application
    sources = Source.objects.all()
    x = np.arange(len(sources))
    # get the number of leads that were converted using the various sources available
    leads = Lead.objects.all()
    source_name = []
    count = []
    for source in sources:
        source_name.append(source.name)
        count.append(leads.filter(source=source).count())
    plt.bar(x, count)
    plt.xticks(x, source_name)

    report_name_src = 'source' + '_{}.png'.format(request.user.username)

    plt.savefig(os.path.join(settings.MEDIA_ROOT, report_name_src))
    plt.close()
    with open(os.path.join(settings.MEDIA_ROOT, 'lead.csv'), mode='w') as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=',', lineterminator='\n', )

        # employee_writer.writerow(['Leads by: {}'.format(request.user.username)])
        employee_writer.writerow(['#', 'Name', 'Location', 'Phone Number', 'Email', 'Description'])
        qs = Lead.objects.filter(trash=False, assigned=request.user).order_by('-pk').all()
        for index, lead in enumerate(qs):
            employee_writer.writerow(
                [
                    '{}'.format(index + 1),
                    '{}'.format(lead.name),
                    '{}'.format(lead.location),
                    '{}'.format(lead.phonenumber),
                    '{}'.format(lead.email),
                    '{}'.format(lead.description)]
            )
    context = {
        'image_status': '/media/' + report_name,
        'image_source': '/media/' + report_name_src,
        'csv': '/media/lead.csv'
    }

    return render(request, 'lead/report.html', context=context)


def genRepo(request, model, name):
    # get the number of sources registered in the application
    sources = model.objects.all()
    x = np.arange(len(sources))
    # get the number of leads that were converted using the various sources available
    leads = Lead.objects.all()
    if name == 'status':
        source_name = []
        count = []
        for source in sources:
            source_name.append(source.name)
            count.append(leads.filter(status=source).count())
    else:
        source_name = []
        count = []
        for source in sources:
            source_name.append(source.name)
            count.append(leads.filter(source=source).count())
    plt.bar(x, count)
    plt.xticks(x, source_name)

    print(len(sources), count, source_name)
    report_name = name + '_{}.png'.format(request.user.username)

    plt.savefig(os.path.join(settings.MEDIA_ROOT, report_name))
    return report_name




def datagenTasks():
    import random
    title = [
        'Checking property accessability', 'client checking', 'calling to confirm client schedule',
        'schedule a meeting with the client', 'product promotion', 'Email the customer'
    ]
    lead = Lead.objects.all()
    description = """
        Nullam ac interdum lectus. Fusce rhoncus dolor vel 
                                 lectus blandit mollis a et nunc. Vivamus laoreet volutpat
                                  molestie. Aliquam nulla sem, elementum varius 
                                  eleifend pretium, maximus eu ipsum. Phasellus et
                                   lacus elementum turpis dignissim varius a accumsan
                                    velit. Quisque eu elit ut augue ultrices dapibus. 
                                    Etiam eleifend ut ipsum a euismod. Nunc dictum eu 
                                    arcu id faucibus. Ut vitae placerat ex, id malesuada 
                                    justo. Sed congue, diam vel blandit gravida, 
                                    purus nisi blandit quam, id viverra mauris neque 
                                    id velit. Nam a interdum orci. Duis a elit eget 
                                    neque dignissim volutpat at pretium dolor.
    """
    for i in lead:
        count = random.randrange(0, 6)
        for _ in range(count):
            tk = Task(
                title=random.choice(title),
                author=i.assigned,
                lead=i,
                description=description
            )
            tk.save()


def datagenLead():
    import random
    from faker import Faker
    status = Status.objects.all()
    source = Source.objects.all()
    users = User.objects.all()
    faker = Faker()
    for _ in range(10):
        ld = Lead(
            status=random.choice(status),
            source=random.choice(source),
            assigned=random.choice(users),
            name=faker.name(),
            phonenumber=faker.phone_number(),
            description="""
                            Lorem ipsum dolor sit amet, consectetur
                             adipiscing elit. Mauris fermentum erat et
                              pretium sagittis. Curabitur et libero ultricies,
                               lacinia diam eu, tempus elit. Nam congue nunc at
                                neque pharetra rutrum. Vivamus vel consequat orci.
                                 Nullam ac interdum lectus. Fusce rhoncus dolor vel 
                                 lectus blandit mollis a et nunc. Vivamus laoreet volutpat
                                  molestie. Aliquam nulla sem, elementum varius 
                                  eleifend pretium, maximus eu ipsum. Phasellus et
                                   lacus elementum turpis dignissim varius a accumsan
                                    velit. Quisque eu elit ut augue ultrices dapibus. 
                                    Etiam eleifend ut ipsum a euismod. Nunc dictum eu 
                                    arcu id faucibus. Ut vitae placerat ex, id malesuada 
                                    justo. Sed congue, diam vel blandit gravida, 
                                    purus nisi blandit quam, id viverra mauris neque 
                                    id velit. Nam a interdum orci. Duis a elit eget 
                                    neque dignissim volutpat at pretium dolor.
                            """
        )
        ld.save()


# schedule automatic email sending


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def sendEmail():
    print(timezone.now().today())
    qs_equal_today = Reminder.objects.filter(dueDate=timezone.now().today(), dueTime__gt=timezone.now().time()).all()
    for object in qs_equal_today:
        if object.email:
            if object.dueTime <= (timezone.now() + timezone.timedelta(seconds=30)).time():
                subject = object.task.title  # task title
                message = object.task.description  # task description
                if object.task.author.email is not None:
                    email = object.task.author.email  # task author.email
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        ['stephenwachira1308@gmail.com', ],
                        fail_silently=False,
                    )
                else: print("cant send email")


# RepeatedTimer(30.0, sendEmail)
