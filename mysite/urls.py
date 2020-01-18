"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from lead import views, forms
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # Lead
    path('', views.LeadListView.as_view(), name="lead_list"),
    path('<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('new/', views.CreateLeadView.as_view(), name='lead_new'),
    path('<int:pk>/edit/', views.LeadUpdateView.as_view(), name='lead_edit'),
    path('<int:pk>/remove/', views.deleteLead, name='lead_remove'),

    # Task
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('task/<int:pk>/createTask/', views.createTask, name='task_create'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('task/<int:pk>/remove/', views.deleteTask, name='task_remove'),

    # Report
    path('report/', views.reports, name='report'),

    # Reminder
    path('reminder/<int:pk>/createReminder/', views.createReminder, name='reminder_create'),


    # Accounts
    url(r'^accounts/login/$', auth_views.LoginView.as_view(authentication_form=forms.UserLoginForm), name='login'),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(), name='logout', kwargs={'next_page': '/'}),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)

