from re import M
from django.shortcuts import render
from comptes.models import University, Ecole, Filiere,Option
from django.http import JsonResponse
from .tools import checkUserType
from django.contrib.auth.models import User
from comptes.models import Memoire
from .tools import getFileContent
from .boyer_moore import plagiarism


def home(request):
    if request.user.username != "":
        user = User.objects.get(username = request.user.username, password=request.user.password) 
        userType = checkUserType(user)
    
    memoires = Memoire.objects.filter(stateAfter=True,activate =True)[:4]
    return render(request,"pages/home.html",locals())

def plagiat(request):
    errorMessage =""
    memoire = Memoire.objects.get(code_memoire = "2021GEI-60034419")
    if request.method == "POST": 
        currentFile = request.FILES["myfile"]
        tempPath  = currentFile.temporary_file_path()
        content = getFileContent(tempPath)
        path = getFileContent(memoire.document.path)
        errorMessage = str(plagiarism(content,path))

    
    return render(request,'plagiat.html',locals())
# AJAX
def load_ecole(request):
    university_id = request.GET.get('university_id')
    ecoles = Ecole.objects.filter(university_id=university_id)
    return JsonResponse(list(ecoles.values('id', 'name')), safe=False)

def load_filiere(request):
    ecole_id = request.GET.get('ecole_id')
    print(ecole_id)
    filieres = Filiere.objects.filter(entity_id=ecole_id)
    return JsonResponse(list(filieres.values('id', 'name')), safe=False)

def load_options(request):
    filiere_id = request.GET.get('filiere_id')
    options = Option.objects.filter(filiere_id=filiere_id)
    return JsonResponse(list(options.values('id', 'name')), safe=False)
