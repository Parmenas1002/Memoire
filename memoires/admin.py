from django.contrib import admin
from .models import Cloture
# Register your models here.

class ClotureAdmin(admin.ModelAdmin):
    list_display = ('ecole','annee','date')

admin.site.register(Cloture,ClotureAdmin)