from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Medicament)
admin.site.register(models.Patient)
admin.site.register(models.Doctor)
admin.site.register(models.Main)
# admin.register(models)