from django.contrib import admin
from .models import Enseignant,Etudiant,Memoire,University,Ecole,Filiere,Option,Agent,Soutenance,Role
# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name','first_name',"inscription_date")
    search_fields = ('last_name','first_name')
    ordering=('last_name',)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name','first_name',"inscription_date")
    list_filter = ('inscription_date',)
    ordering=('last_name',)

class MemoireAdmin(admin.ModelAdmin):
    list_display = ('topic','academicYear','supervisor','etudiants','depositDay')
    list_filter = ('supervisor','academicYear','mention')

class AgentAdmin(admin.ModelAdmin):
    list_display = ('user','ecole','code_agent','inscription_date')

class SoutenanceAdmin(admin.ModelAdmin):
    list_display = ('memoire', 'jury_number','place','date_planned')

class RoleAdmin(admin.ModelAdmin):
    list_display = ('soutenance','teacher','role')

admin.site.register(University)
admin.site.register(Ecole)
admin.site.register(Filiere)
admin.site.register(Option)
admin.site.register(Agent,AgentAdmin)
admin.site.register(Memoire,MemoireAdmin) 
admin.site.register(Etudiant,StudentAdmin)
admin.site.register(Enseignant,TeacherAdmin)
admin.site.register(Soutenance,SoutenanceAdmin)
admin.site.register(Role,RoleAdmin)

