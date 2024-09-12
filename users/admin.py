from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import *


class CustomUserAdmin(UserAdmin):
    list_display = ['username', ]
    search_fields = ('username',)
    model = User

UserAdmin.fieldsets += ('', {'fields': ('roleOfEmployee',)}),
admin.site.register(User, CustomUserAdmin)