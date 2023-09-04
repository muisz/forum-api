from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'username', 'is_active', 'date_joined')
    search_fields = ('first_name', 'last_name', 'username')


admin.site.register(User, UserAdmin)
