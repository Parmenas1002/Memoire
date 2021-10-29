from comptes.models import Enseignant,Etudiant,Agent,Ecole,Memoire,Academic_year,Soutenance,Role
from django.shortcuts import get_object_or_404
from random import choice
import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import re
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings
from django.contrib.auth.models import User
import os
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams,LTFigure,LTTextBox
from pdfminer.pdfdocument import PDFDocument 
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
import PyPDF2



def checkUserType(user):
    userType = 0
    try:
        student = Etudiant.objects.get(user = user)
    except Etudiant().DoesNotExist:
        try :
            teacher = Enseignant.objects.get(user= user)
        except Enseignant().DoesNotExist:
            try :
                agent = Agent.objects.get(user= user)
            except Agent().DoesNotExist:
                userType = 0
            else :
                userType = 3
        else :
            userType = 2
    else:
        userType = 1
    return userType

def generate_id(n=8):
    alphabet = [ chr(i) for i in range(65,123) if i!= 91 and i!= 92 and i!= 93 and i!= 94 and i!= 95 and i!= 96]
    id = ''
    for i in range(n):
        id += choice(alphabet)    
    return id

def generate_code(memoire):
    acad = memoire.academicYear.titre.split('-')[1]
    filiere = memoire.filiere.name
    students = memoire.get_list_students()
    student_char_list = ""
    i=0
    for student in students:
        if i==0 :            
            student_char_list += str(student.user.username)
        else :
            student_char_list += "-" + str(student.user.username)
        i=i+1
    code = acad + filiere + "-"+ student_char_list

    return code

def ckeck_date(compareDate):
    currentDate = datetime.datetime.now().date()
    if currentDate > compareDate:
       return True
    else :
        return False

def verification(user):
    currentStudent= Etudiant()
    try:
        currentStudent = Etudiant.objects.get(user = user)                        
    except  Etudiant().DoesNotExist:    
        return False
    else: 
        return True  

def getStudent(username,password):
    user = authenticate(username = username, password = password)
    currentStudent = Etudiant.objects.get(user = user)
    return currentStudent

def patnerVerification(username,password,currentStudent):
    user = User()
    user = authenticate(username = username, password = password)
    if user == None :
        return False, "Les identifiants de votre partenaire sont incorrects."
    else :
        student_verify = verification(user)
        if student_verify == True:
            if currentStudent == user:
                return False, "Impossible de vous associer encore à ce même dépôt."
            else :
                return True, "Un autre étudiant a été bien ajouté."
        else:
            return False, "Les identifiants de votre partenaire sont incorrects."

def createList(line,dataset):
    error = False
    lastName = "",
    email =""
    fisrtName = ""
    message = []
    try :
        lastName = dataset[line][0].upper() 
    except AttributeError:
        message.append("Aucun nom sur la ligne numéro {}".format(line+2))   
    else :
        pass

    try :
        fisrtName = dataset[line][1].capitalize()  
    except AttributeError:
        message.append("Aucun prénom sur la ligne numéro {}".format(line+2))   
    else :
        pass

    try :
        email = dataset[line][2].lower()   
    except AttributeError:
        message.append("Aucun mail sur la ligne numéro {}".format(line+2))   
    else :
        pass
    
    password = dataset[line][3]
    if lastName!= "" and fisrtName != "" and email !="" :
        informations = [lastName,fisrtName,password]
        return False, message, {email:informations}
    else :
        return True, message,{}

def sendemail(currentUser,password,email_title):
    receiver_mail = currentUser.user.email
    context = {'currentUser' : currentUser,'password':password}
    email_html_template = get_template("email/teacher.html").render(context)
    email_msg = EmailMessage(email_title,email_html_template,settings.EMAIL_HOST_USER,[receiver_mail])
    email_msg.content_subtype = 'html'
    email_msg.send(fail_silently=False)

def sendPmail(currentUser):
    receiver_mail = currentUser.user.email
    context = {'currentUser' : currentUser,'cAcad':Academic_year.objects.last()}
    email_html_template = get_template("email/plan_teacher.html").render(context)
    email_msg = EmailMessage("Planification des soutenances",email_html_template,settings.EMAIL_HOST_USER,[receiver_mail])
    email_msg.content_subtype = 'html'
    email_msg.send(fail_silently=False)


def addTeacher(teachers_list):
    for teacher_info in teachers_list:
        for key, value in teacher_info.items():
            user = User.objects.create_user(username = value[1],email = key,password = value[2])
            newTeacher = Enseignant.objects.create(user = user)
            newTeacher.last_name = value[0]
            newTeacher.first_name = value[1]
            newTeacher.save()
            ecole = get_object_or_404(Ecole, id=1)
            newTeacher.ecole.add(ecole)
            newTeacher.save()
            sendemail(newTeacher,value[2],"Enrégistrement sur la plateforme e-Memoire")
            
def get_count(memoires, valid_memoire):
    total = len(memoires)
    valid = len(valid_memoire)
    no_valid = total - valid
    return total, valid, no_valid   
    
def ckeckusername(username):
    error = False
    errorMessage = ""
    user = User()
    try:
        user = User.objects.get(username=username)
    except User().DoesNotExist:
        pass
    else :
        error = True
        errorMessage  = "Un utilisateur possède déjà ce nom d'utilisateur."   
    return error, errorMessage

def checkusermail(email):
    print(email)
    error = False
    errorMessage = ""
    try:
        user = User.objects.get(email=email)
    except User().DoesNotExist:
        pass
    else :
        error = True
        errorMessage  = "Un utilisateur possède déjà cette addresse mail."
    return error, errorMessage

def deleteFile(path):
    if os.path.exists(path):
        os.remove(path)
        return True
    else :
        return False

def control_deposit(student,ecole):
    currentAcad = Academic_year.objects.last()
    try :
        memoire = student.memoire.get(filiere__entity = ecole,academicYear = currentAcad)
    except Memoire().DoesNotExist:
        return False, ""
    else :
        return True, "Impossible d'enrégistrer votre dépôt. Vous n'êtes autorisés à effectuer qu'un seul dépôt de mémoire dans une école au titre d'une anée académique. "

def control_depositTwo(student,ecole,binome):
    currentAcad = Academic_year.objects.last()
    try :
        memoire = student.memoire.get(filiere__entity = ecole,academicYear = currentAcad)
    except Memoire().DoesNotExist:
        try :
            memoire = binome.memoire.get(filiere__entity = ecole,academicYear = currentAcad)
        except Memoire().DoesNotExist:
            return False, ""
        else :
            return True, "Impossible d'enrégistrer votre dépôt. Votre binôme a déjà effectué un dépôt dans cette école pour le compte de cette année académique."
    else :
        return True, "Impossible d'enrégistrer votre dépôt. Vous avez déjà effectué un dépôt dans cette école pour le compte de cette année académique."


def addSoutenance(dataset):
    i = 0
    mailList = []
    for line in dataset:
        new_soutenance = Soutenance()
        new_memoire = Memoire.objects.get(code_memoire = line[0])
        jury = int(line[1])
        myDate = line[2]
        place = line[3]
        new_soutenance.memoire = new_memoire
        new_soutenance.jury_number = jury
        new_soutenance.date_planned = myDate
        new_soutenance.place = place
        new_soutenance.save()
        for student in new_memoire.get_list_students():
            if not student in mailList:
                mailList.append(student)

        for mail in line[4].split(','):
            teacher = Enseignant.objects.get(user__email = mail)
            if i == 0:
                role = Role.objects.create(soutenance = new_soutenance,teacher = teacher,role = 1)
            else :
                role = Role.objects.create(soutenance = new_soutenance,teacher = teacher,role = 2)
            if not teacher in mailList:
                mailList.append(teacher)
            i = i+1
        i=0
    for user in mailList:
        sendPmail(user)
    
def getFileContent(path):
    text = ""
    start = False
    end = False
    with open (path,'rb') as f:
        parser = PDFParser(f)
        pdfReader = PyPDF2.PdfFileReader(f)
        numPages = pdfReader.numPages
        print(numPages)
        doc = PDFDocument(parser)
        for i in range(7,numPages):
            page = list(PDFPage.create_pages(doc))[i]
            manager = PDFResourceManager()
            device = PDFPageAggregator(manager, laparams=LAParams())
            interpreter = PDFPageInterpreter(manager,device)
            interpreter.process_page(page)
            layout = device.get_result()
            for obj in layout :
                if isinstance(obj,LTTextBox):
                    if obj.get_text().strip() == "INTRODUCTION":
                        start = True
                    if start == True and end == False:
                        text = text + obj.get_text()
                    if obj.get_text().strip() == "CONCLUSION":
                        end = True
    lTest =text.split()
    content = ' '.join(map(str,lTest))
    print(content)
    return content
        