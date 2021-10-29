from django.urls import path
from . import views

urlpatterns = [
    path('inscription-etudiant-2.0/',views.registerStudent, name = "registerStudent"), 
    path("connexion-etudiant-2.0/", views.loginUser, name="loginUser"),
    path("connexion-enseignant-2.0/", views.loginTeacher, name="loginTeacher"),
    path("tableau-de-bord-etudiant-2.0/<message>",views.dashboardStudent, name = "dashboardStudent"),
    path('logout/',views.logoutUser,name = 'logout'),
    path('inscription-enseignant-2.0',views.registerTeacher,name = "registerTeacher"),
    path("tableau-de-bord-enseignant-2.0/<message>",views.dashboardTeacher, name = "dashboardTeacher"),
    path("tableau-de-bord-agent-2.0",views.dashboardAgent, name = "dashboardAgent"),
    path('profile-student-2.0/',views.profileStudent,name = 'profileStudent'),
    path('profile-enseignant-2.0/',views.profileTeacher,name = 'profileTeacher'),
    path('modification-mot-de-passe/',views.changePass,name = 'changePassword'),
    path('liste-enseignants/',views.listTeacher,name = 'listTeacher'),
    path('liste-soutenance/',views.listSoutenance,name = 'listSoutenance'),
    
]