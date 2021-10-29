from django.core.mail import message
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import StudentRegister,LoginForm,AddEntity,AddAvatarForm,ModifInfo,LoginTForm,PlandocForm
from .models import Agent, Enseignant, Etudiant, Memoire,Academic_year,Ecole,Soutenance,Role
from django.contrib.auth.models import User
from random import choice
from eMemoire.tools import checkUserType,generate_code,ckeck_date,addTeacher,createList,get_count,ckeckusername,checkusermail,generate_id,ckeck_date,addSoutenance
from memoires.models import Cloture
from tablib import Dataset
from django.contrib import messages
import datetime
from .backends import EmailBackend

#====================== Variables
currentAcademicYear = Academic_year.objects.last()

# Views
def registerStudent(request):  
    if request.user.username != "":
        user = User.objects.get(username = request.user.username, password=request.user.password) 
        userType = checkUserType(user)
    errorMessage = ""
    register= False
    form = StudentRegister(request.POST or None)
    if form.is_valid():
        user = User()
        try:
            print(form.cleaned_data['username'])
            user = User.objects.get(username=form.cleaned_data['username'])
        except user.DoesNotExist:
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
            except user.DoesNotExist:
                user = User.objects.create_user(form.cleaned_data['username'],form.cleaned_data['email'], form.cleaned_data['password'])
                newStudent = Etudiant.objects.create(user = user)
                newStudent.last_name = form.cleaned_data['name']
                newStudent.first_name = form.cleaned_data['firstName']
                newStudent.save() 
                register=True
            else :
                errorMessage  = "Un étudiant possède déjà cette addresse mail."
        else :
            errorMessage  = "Un étudiant possède déjà ce numéro matricule"                          
    if register == True :
        login(request,user,backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboardStudent', message = "register-sucesss")  
 
    return render(request,"comptes/inscript_etudiant.html",locals())

def loginUser(request):
    if request.user.username != "":
        user = User.objects.get(username = request.user.username, password=request.user.password) 
        userType = checkUserType(user)
    errorMessage = "" 
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = User()            
        try:
            user = User.objects.get(username=username)
        except user.DoesNotExist:
            errorMessage = "Aucun étudiant n'a été enregistré avec ce numéro matricule."
        else :
            user = authenticate(username = username,password = password)
            if user == None :
                errorMessage = "Votre mot de passe est incorrect."
            else :
                login(request,user,backend='django.contrib.auth.backends.ModelBackend')
                userType = checkUserType(user)
                if userType == 1 :    
                    return redirect('dashboardStudent',message = "login-sucess")
                elif userType == 3 :
                    return redirect ('dashboardAgent')
                else :
                    errorMessage = "Une erreur a été détecté avec ses identifiants. Rapprochez vous de votre administration pour obtenir des solutions. "
                               
    return render(request,"comptes/connexion.html",locals())

def loginTeacher(request):
    if request.user.username != "":
        user = User.objects.get(username = request.user.username, password=request.user.password) 
        userType = checkUserType(user)
    errorMessage = ""
    form = LoginTForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = User()            
        try:
            user = User.objects.get(email=email)
            print(user)
        except user.DoesNotExist:
            errorMessage = "Aucun enseignant n'a été enregistré avec cette adresse mail."
        else :
            user = authenticate(username = email,password = password)
            if user == None :
                errorMessage = "Votre mot de passe est incorrect."
            else :
                userType = checkUserType(user)
                if userType == 2 :
                    login(request,user,backend='comptes.backends.EmailBackend')
                    return redirect('dashboardTeacher',message = "login-sucess")
                else :
                    errorMessage = "Seuls les enseignants sont autorisés à se connecter à partir de ce formulaire."
                           
    return render(request, "comptes/connexion_enseignant.html",locals())

@login_required
def dashboardStudent(request,message):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentStudent = Etudiant.objects.get(user = user)
    alertMessage = ""
    if message == "login-sucess" :
        alertMessage = "Heureux de vous revoir {} ".format(currentStudent.first_name)
    elif message == "register-sucesss":
        alertMessage = "{} Bienvenue sur e-Memoire ".format(currentStudent.first_name)
    elif message == "delete-success":
        alertMessage = "Dépôt de Mémoire supprimé avec succès."
    elif message == "deposit-success":
        alertMessage = "Votre dépôt de mémoire a été bien enrégistré."
    currentAcad = currentAcademicYear
    
    lenM = len(currentStudent.memoire.all())
    studentmemoires = currentStudent.memoire.filter(activate =True,academicYear = currentAcademicYear)
    valid_memoires = currentStudent.memoire.filter(activate =True,stateBefore = True,academicYear = currentAcademicYear)
    total,valid, no_valid = get_count(studentmemoires, valid_memoires) 
    
    return render(request, "comptes/dashEtudiant.html",locals())

@login_required
def dashboardTeacher(request,message):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentTeacher = Enseignant.objects.get(user = user)    
    currentAcad = currentAcademicYear
    exist_memoire = False
    memoires = QuerySet()
    roles = Role.objects.filter(teacher = currentTeacher)
    roles_valid = Role.objects.filter(teacher = currentTeacher, soutenance__memoire__stateAfter = True)
    if len(roles) >0 :
        exist_memoire = True
    total,valid, no_valid = roles.count(),roles_valid.count(),(roles.count()-roles_valid.count())
    alertMessage = ""
    if message == "login-sucess" :
        alertMessage = "Heureux de vous revoir Mr/Mme {} {} ".format(currentTeacher.first_name,currentTeacher.last_name)
  
    return render(request, 'comptes/dashEnseignant.html',locals())

@login_required
def dashboardAgent(request):
    successMessage = ""
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentAgent = Agent.objects.get(user = user)  
    currentAcad = currentAcademicYear
    currentDepositDay = Cloture.objects.get(ecole = currentAgent.ecole)
    memoires = Memoire.objects.filter(filiere__entity = currentAgent.ecole,academicYear = currentAcad)
    valid_memoires = Memoire.objects.filter(filiere__entity = currentAgent.ecole,stateBefore = True,academicYear = currentAcad)
    total,valid, no_valid = get_count(memoires, valid_memoires) 

    if request.method == "POST":
        if "depSubmit" in request.POST :
            myDate = datetime.datetime.strptime(request.POST["depositDate"], "%Y-%m-%d").date()
            currentDepositDay.date = myDate
            currentDepositDay.save()
            successMessage = "Nouvelle date enrégistrée avec succès."
    return render(request, 'comptes/dashAgent.html',locals())

@login_required
def profileStudent(request):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentStudent = Etudiant.objects.get(user = user)
    memoires = currentStudent.memoire.filter(activate =True)
    valid_memoires = currentStudent.memoire.filter(activate =True,stateAfter = True)
    total,valid, no_valid = get_count(memoires, valid_memoires) 
    errorMessage = ""
    successMesage = ""
    valid_avatar = False
    valid_info = False
    principal_error = False
    avartarForm = AddAvatarForm()
    changeInfo = ModifInfo()
    if request.method == 'POST':    
        if "change_avatar" in request.POST :
            avartarForm = AddAvatarForm(request.POST,request.FILES)
            if avartarForm.is_valid():
                avatar = avartarForm.cleaned_data['avatar']
                if avatar != None :
                    currentStudent.avatar = avatar
                    currentStudent.save()
                    valid_avatar = True
        if "change_info" in request.POST :
            changeInfo = ModifInfo(request.POST)
            if changeInfo.is_valid():
                username = changeInfo.cleaned_data['username']
                firstName = changeInfo.cleaned_data['firstName']
                name = changeInfo.cleaned_data['name']
                email = changeInfo.cleaned_data['email']
                if name != "":
                    currentStudent.last_name = name
                    valid_info = True  
                if firstName!= "":
                    currentStudent.first_name = firstName
                    valid_info = True
                if email!= "":
                    error, message = checkusermail(email)
                    if error== True :
                        errorMessage = message
                        principal_error = True
                    else :
                        user.email = email
                        valid_info = True
                if username != "":
                    errorU, messageU = ckeckusername(username)
                    if errorU== True :
                        errorMessage = messageU
                        principal_error = True
                    else :
                        user.username = username
                        valid_info = True
                    
                currentStudent.save()
                user.save()
                update_session_auth_hash(request, user)  # Important!
            
    if valid_avatar == True :
        successMesage = "Avatar Modifié avec succès." 
        print(successMesage)
    if valid_info == True and principal_error == False:
        successMesage = "Informations modifiées avec succès"
    
    return render(request, "comptes/profileStudent.html",locals())

@login_required
def profileTeacher(request):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentTeacher = Enseignant.objects.get(user = user)
    roles = Role.objects.filter(teacher = currentTeacher)
    roles_valid = Role.objects.filter(teacher = currentTeacher, soutenance__memoire__stateAfter= True)
    total,valid, no_valid = get_count(roles, roles_valid) 
    errorMessage = ""
    successMesage = ""
    valid_avatar = False
    valid_info = False
    principal_error = False
    avartarForm = AddAvatarForm()
    changeInfo = ModifInfo()
    if request.method == 'POST':    
        if "change_avatar" in request.POST :
            avartarForm = AddAvatarForm(request.POST,request.FILES)
            if avartarForm.is_valid():
                avatar = avartarForm.cleaned_data['avatar']
                if avatar != None :
                    currentTeacher.avatar = avatar
                    currentTeacher.save()
                    valid_avatar = True
        
            
    if valid_avatar == True :
        successMesage = "Avatar Modifié avec succès." 
        print(successMesage)
    if valid_info == True and principal_error == False:
        successMesage = "Informations modifiées avec succès"
    
    return render(request, "comptes/profileTeacher.html",locals())

def changePass(request):
    user = User.objects.get(username = request.user.username, password=request.user.password) 
    userType = checkUserType(user)
    changePassForm = PasswordChangeForm(user= request.user)
    if request.method == "POST":
        changePassForm = PasswordChangeForm(request.user,request.POST)
        if changePassForm.is_valid():
            user = changePassForm.save()
            update_session_auth_hash(request, user)  # Important! 
            if userType == 1 :
                return redirect('dashboardStudent',message = "change-password")
            elif userType == 2:
                return redirect ('dashboardTeacher')
            elif userType == 3 :
                return redirect ('dashboardAgent')
        
    return render(request, "comptes/changePassword.html",locals())

def logoutUser(request):
    logout(request)
    return redirect('loginUser')
    
def registerTeacher(request):
    if request.user.username != "":
        user = User.objects.get(username = request.user.username, password=request.user.password) 
        userType = checkUserType(user)
    errorMessage = ""
    teachers_list = []
    principal_error = False
    if request.method == "POST": 
        dataset = Dataset()
        new_persons = request.FILES["myfile"]
        import_data = dataset.load(new_persons.read())
        code = [generate_id() for i in range(len(dataset))]
        dataset.append_col(code,header="Mot de passe")
        print(dataset)
        print(dataset[0])
        for i in range(len(dataset)):
            error, message ,teacher = createList(i,dataset)
            if error == True :
                errorMessage = message[0]
                principal_error = True
                break
            else:
                teachers_list.append(teacher)
        print(teachers_list)
        if principal_error == False :
            addTeacher(teachers_list)
           
    return render(request,"comptes/inscript_enseignant.html",locals())

def listTeacher(request):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentAgent = Agent.objects.get(user = user)  
    teachers = Enseignant.objects.filter(ecole = currentAgent.ecole)
    return render(request, "comptes/listeEnseignant.html",locals())

def listSoutenance(request):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentAgent = Agent.objects.get(user = user)  
    soutenances = Soutenance.objects.filter(memoire__filiere__entity = currentAgent.ecole)
    form = PlandocForm()
    errorMessage = ""
    successMesage = ""
    if request.method == "POST": 
        dataset = Dataset()
        new_soutenances = request.FILES["myfile"]
        import_data = dataset.load(new_soutenances.read())
        addSoutenance(dataset)
    return render(request, "comptes/soutenance.html",locals())