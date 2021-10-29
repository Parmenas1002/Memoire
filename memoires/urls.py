from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name = "memoire_index"),
    path('depot-memoire-2.0-1',views.depositOne, name = "depositOne"),
    path('depot-memoire-2.0-2',views.depositTwo, name = "depositTwo"),
    path('détails-etudiant-2.0/<code_memoire>',views.viewStudent, name = "viewStudent"),
    path('détails-enseignant-2.0/<code_memoire>',views.viewTeacher, name = "viewTeacher"),
    path('détails-memoire-public-2.0/<code_memoire>',views.viewPublic, name = "viewPublic"),
    path('détails-agent-2.0/<code_memoire>',views.viewAgent, name = "viewAgent"),
    
]