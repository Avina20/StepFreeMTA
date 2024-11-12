from django.contrib import admin

# Register your models here.
from .models import Message, BlockedUser

admin.site.register(Message)
admin.site.register(BlockedUser)
