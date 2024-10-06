from django.contrib import admin

from testapp.models import Spare, Machine, Kit

admin.site.register(Spare)
admin.site.register(Machine)
admin.site.register(Kit)
