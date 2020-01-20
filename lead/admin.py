from django.contrib import admin
from .models import Lead, Status, Source, Task, Profile
# Register your models here.
admin.site.register(Status)
admin.site.register(Source)
admin.site.register(Task)
admin.site.register(Profile)
admin.site.register(Lead)
