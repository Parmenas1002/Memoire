from django.shortcuts import render,redirect,get_object_or_404
from eMemoire.tools import checkUserType, generate_code
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from comptes.models import Enseignant, Filiere, Memoire,Etudiant,Academic_year,Agent, Role, Soutenance,Comment
from django.contrib.auth.decorators import login_required
from .forms import EndOne,EndTwo, DepositOne, DepositTwo,ModifyDocument,AddTInfo,AddComment, StudentModifForm
from eMemoire.tools import patnerVerification,getStudent,ckeck_date,deleteFile,control_deposit,control_depositTwo,getFileContent
from .models import Cloture
from eMemoire.boyer_moore import plagiarism

currentAcadmicYear = Academic_year.objects.last()

# Create your views here.

def index(request):
    if request.user.username != "":
        user = User.objects.get(username = request.user.username, password=request.user.password) 
        userType = checkUserType(user)
        
    memoires = Memoire.objects.filter(stateAfter=True,activate =True)
    page = request.GET.get('page', 1)      
    paginator = Paginator(memoires, 10)
    try:
        memoires = paginator.page(page)
    except PageNotAnInteger:
        memoires = paginator.page(1)
    except EmptyPage:
        memoires = paginator.page(paginator.num_pages)
    if request.method == 'POST':    
        print(request)
    return render (request, "memoires/index.html",locals())



@login_required
def depositOne(request):
    user = User.objects.get(username = request.user.username, password=request.user.password) 
    currentStudent = Etudiant.objects.get(user = user)
    errorMessage = ""
    errordetection =""
    deposit =False 
    new_memoire = Memoire()
    new_memoire.academicYear = currentAcadmicYear
    if request.method == 'POST':
        form =  DepositOne(request.POST,request.FILES)
        if form.is_valid():   
            cloture = Cloture.objects.get(ecole = form.cleaned_data['ecole'])
            depot = ckeck_date(cloture.date)
            if depot == True :
                errorMessage = "Le délai pour les dépôts dans cette école est expiré."
            else :
                existM, message = control_deposit(currentStudent,form.cleaned_data['filiere'].entity)
                if existM == True :
                    errorMessage = message
                else :
                    tempPath  = form.cleaned_data['document'].temporary_file_path()
                    content = getFileContent(tempPath)
                    compareMemoire = Memoire.objects.get(code_memoire = "2021GEI-60034419")
                    compareText = getFileContent(compareMemoire.document.path)
                    rate = plagiarism(compareText,content)
                    if rate >= 25.0 :
                        errordetection ="Plagiat détecté avec le mémoire de " + compareMemoire.etudiants +" sous le thème " + compareMemoire.topic
                    else :
                        new_memoire.filiere = form.cleaned_data['filiere']
                        new_memoire.option = form.cleaned_data['option']
                        new_memoire.topic = form.cleaned_data['topic']
                        new_memoire.supervisor = form.cleaned_data['supervisor']
                        new_memoire.document = form.cleaned_data['document']                          
                        new_memoire.save()
                        currentStudent.memoire.add(new_memoire)
                        currentStudent.save() 
                        new_memoire.code_memoire = generate_code(new_memoire)
                        new_memoire.save()  
                        deposit = True      
    else :
        form =  DepositOne()
    if deposit ==True:
        return redirect('dashboardStudent',message = "deposit-success")
        
    return render(request, "memoires/depositOne.html",locals())
@login_required
def depositTwo(request):
    user = User.objects.get(username = request.user.username, password=request.user.password) 
    currentStudent = Etudiant.objects.get(user = user)
    errorMessage = ""
    errordetection =""
    envoi =False 
    new_memoire = Memoire()
    new_memoire.academicYear = currentAcadmicYear
    if request.method == 'POST':
        form = DepositTwo(request.POST,request.FILES)
        if form.is_valid():
            cloture = Cloture.objects.get(ecole = form.cleaned_data['ecole'])
            depot = ckeck_date(cloture.date)
            if depot == True :
                errorMessage = "Le délai pour les dépôts dans cette école est expiré."
            else :
                indicator, message = patnerVerification(form.cleaned_data['patnerUsername'],form.cleaned_data['patnerPassword'],user)
                print(indicator,message)
                if indicator == False:
                    errorMessage = message
                else :
                    patner = getStudent(form.cleaned_data['patnerUsername'],form.cleaned_data['patnerPassword'])
                    existM, message = control_depositTwo(currentStudent,form.cleaned_data['filiere'].entity,patner)
                    if existM == True :
                        errorMessage = message
                    else :
                        new_memoire.filiere = form.cleaned_data['filiere']
                        new_memoire.option = form.cleaned_data['option']
                        new_memoire.topic = form.cleaned_data['topic']
                        new_memoire.supervisor = form.cleaned_data['supervisor']
                        new_memoire.document =   form.cleaned_data['document']                        
                        new_memoire.save()
                        currentStudent.memoire.add(new_memoire)
                        patner.memoire.add(new_memoire)
                        patner.save() 
                        currentStudent.save() 
                        new_memoire.code_memoire = generate_code(new_memoire)
                        new_memoire.save() 
                        envoi = True          
    else :
        form = DepositTwo()
    if envoi ==True:
        return redirect('dashboardStudent',message = "deposit-success") 
    return render(request, "memoires/depositTwo.html",locals())

@login_required
def viewStudent(request,code_memoire):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentStudent = Etudiant.objects.get(user = user)
    memoire = get_object_or_404(Memoire, code_memoire=code_memoire)
    errorMessage = ""
    successMesage = ""
    modification = False
   
    prevDocPath = memoire.document.path
    docForm = ModifyDocument()
    modifForm = StudentModifForm()
    if request.method == "POST":
        if "changeDoc" in request.POST :
            docForm = ModifyDocument(request.POST,request.FILES)
            print("Le document peut est modifié")
            if docForm.is_valid():
                delete = deleteFile(prevDocPath)
                if delete :
                    memoire.document = docForm.cleaned_data['document']
                    memoire.save()
                    modification = True
                else :
                    errorMessage = "Impossible d'enrégister votre document."
        if "delete_yes" in request.POST :
            deleteT = deleteFile(prevDocPath)
            if deleteT:
                memoire.delete()
                return redirect("dashboardStudent",message = "delete-success")
        if "modif" in request.POST:
            modifForm = StudentModifForm(request.POST,request.FILES)
            if modifForm.is_valid():
                memoire.presentationImage = modifForm.cleaned_data['presentationImage']
                memoire.abstract = modifForm.cleaned_data['abstract']
                memoire.save()
                successMesage = "Image et Résumé ajouté avec succès."


        

    return render(request,"memoires/view_student.html",locals())

def viewTeacher(request,code_memoire):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentTeacher = Enseignant.objects.get(user = user)
    memoire = get_object_or_404(Memoire, code_memoire=code_memoire)
    role = Role.objects.get(soutenance__memoire = memoire, teacher= currentTeacher)
    comments = Comment.objects.filter(memoire = memoire,teacher = currentTeacher)
    new_comment = Comment()
    successMesage= ""
    errorMessage = ""
    addCommentForm = AddComment()
    if role.role == 1 :
        form = AddTInfo()
        if request.method == 'POST':
            if 'validate' in request.POST :
                form = AddTInfo(request.POST)
                if form.is_valid():           
                    if form.cleaned_data['middleClass'] <=10 :
                        errorMessage = "Veuillez revoir la note de l'étudiant."
                    else :
                        memoire.middleClass = form.cleaned_data['middleClass']
                        memoire.mention = form.cleaned_data['mention']
                        memoire.save()
                        successMesage = "Moyenne et mention ajoutée avec succès."
    if request.method == 'POST':
        if 'add_comment' in request.POST :  
            print("Yes")          
            addCommentForm = AddComment(request.POST)
            if addCommentForm.is_valid():
                new_comment.title = addCommentForm.cleaned_data['title']
                new_comment.content = addCommentForm.cleaned_data['content']
                new_comment.teacher = currentTeacher
                new_comment.memoire = memoire
                new_comment.save()   
                successMesage = "Nouveau commentaire ajouté avec succès."
        
    return render(request,"memoires/view_teacher.html",locals())

@login_required
def viewAgent(request,code_memoire):
    user = User.objects.get(username = request.user.username, password=request.user.password)      
    currentAgent = Agent.objects.get(user = user) 
    memoire = get_object_or_404(Memoire, code_memoire=code_memoire)

    if request.method == "POST": 
        if "deactivate_yes" in request.POST :
            memoire.activate = False
            memoire.save()
            return redirect("dashboardAgent")
        if "activate_yes" in request.POST:
            memoire.activate = True
            memoire.save()
            return redirect("dashboardAgent")


    return render(request,"memoires/view_agent.html",locals())

def viewPublic(request,code_memoire):
    if request.user.username != "":
        user = User.objects.get(username = request.user.username, password=request.user.password) 
        userType = checkUserType(user)
    memoire = get_object_or_404(Memoire, code_memoire=code_memoire)
    roles = Role.objects.filter(soutenance__memoire = memoire)
    return render(request, "memoires/oneMemoire.html",locals())