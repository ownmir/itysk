from django.contrib import admin
from . import models


class MainAdmin(admin.ModelAdmin):
    list_filter = ('patient',)


# Register your models here.
admin.site.register(models.Medicament)
admin.site.register(models.Patient)
admin.site.register(models.Doctor)
admin.site.register(models.Main, MainAdmin)


