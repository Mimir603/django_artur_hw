from django.contrib import admin

from testapp.models import Spare, Machine, Kit, Img

admin.site.register(Spare)
admin.site.register(Machine)
admin.site.register(Kit)
admin.site.register(Img)
