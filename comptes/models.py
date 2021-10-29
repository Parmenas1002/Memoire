from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
import datetime
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from random import choice
#===================Variables

def generate_id(n=10):
    alphabet = [ chr(i) for i in range(65,123) if i!= 91 and i!= 92 and i!= 93 and i!= 94 and i!= 95 and i!= 96]
    id = ''
    for i in range(n):
        id += choice(alphabet)    
    return id

MENTION_OPTIONS = (
    ('Passable','Passable'),
    ('Assez-bien','Assez-bien'),
    ('Bien','Bien'),
    ('Très-bien','Très-bien'),
    ('Excellente','Excellente')
)

# Models are Yere

class University(models.Model):
    name = models.CharField(max_length=110, verbose_name= "Intitulé de l'Université")

    class Meta():
        verbose_name = "Université"
        ordering = ['name']    
    def __str__(self):
        return self.name

######
class Ecole(models.Model):
    name = models.CharField(max_length=110, verbose_name= "Intitulé de le l'école/Institut/Faculté")
    university = models.ForeignKey(University, on_delete= models.CASCADE,verbose_name= "Université")

    class Meta():
        verbose_name="Ecole/Institut/Faculté"
        ordering = ['name']

    def __str__(self):
        return self.name  

class Filiere(models.Model):
    name = models.CharField(max_length=40, verbose_name="Intitulé de la Filière")
    entity = models.ForeignKey(Ecole, on_delete = models.CASCADE, verbose_name ="Ecole/Institut/Faculté")

    class Meta():
        verbose_name = "Filière"
        ordering = ['name']

    def __str__(self):
        return self.name

class Option(models.Model):
    name = models.CharField(max_length=40,verbose_name="Option")
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE,verbose_name="Filière")

    class Meta():
        ordering = ['filiere__name']

    def __str__(self):
        return  self.name
class Academic_year (models.Model):
    titre = models.CharField(max_length=40,verbose_name="Année")
    
    class Meta():
        verbose_name = "Année Académique"
    def __str__(self) :
        return self.titre

class Enseignant(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    last_name= models.CharField(max_length=100,verbose_name="Nom")
    first_name = models.CharField(max_length=100,verbose_name="Prénom")
    avatar = models.ImageField(default = 'default.png',upload_to = 'avatar/',null=True, blank=True)
    inscription_date = models.DateTimeField(auto_now_add=True,verbose_name="Date d'Inscription")
    ecole = models.ManyToManyField(Ecole,blank=True, null = True)
   
    class Meta():
        verbose_name = "Enseignant"

    def get_soutenances(self):
        return self.soutenance_set.all()

    def __str__(self):
        return "Enseignant " + self.last_name + " " + self.first_name

class Agent(models.Model):
    user = models.OneToOneField(User, default= 0, on_delete = models.CASCADE,verbose_name="Utilisateur")
    ecole = models.ForeignKey(Ecole, on_delete=models.SET_NULL, blank=True, null=True,verbose_name="Ecole") 
    code_agent = models.CharField(max_length=20, verbose_name="Code Agent", blank=True, null=True)
    inscription_date = models.DateTimeField(auto_now_add=True,verbose_name="Date d'Inscription")
      
    class Meta():
        verbose_name = "Agent du Secrétariat"
    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if self.code_agent == None :
            self.code_agent = generate_id()
        else :
            print("Un code a déja été attribué")

        super().save(*args, **kwargs)

class Memoire(models.Model):
    topic = models.CharField(max_length=220,verbose_name="Thème du mémoire",blank=True, null=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, blank=True, null=True,verbose_name="Filière")
    option = models.ForeignKey(Option, on_delete=models.SET_NULL, blank=True, null=True)
    academicYear = models.ForeignKey(Academic_year,on_delete=models.SET_NULL,verbose_name="Année Académique",blank=True, null=True)
    code_memoire = models.CharField(max_length=100,verbose_name="Code Mémoire",blank=True, null=True)
    supervisor = models.CharField(max_length=120,verbose_name="Superviseur",blank=True, null=True)
    middleClass = models.FloatField(default=0, verbose_name="Note obtenue",null=True, blank=True)
    mention = models.CharField(max_length=20, verbose_name="Mention",choices=MENTION_OPTIONS,null=True, blank=True)
    activate = models.BooleanField(default=True,verbose_name="Memoire Active/Désactive")
    stateBefore = models.BooleanField(default=False,verbose_name="Statut avant la Soutenance")
    stateAfter = models.BooleanField(default=False, verbose_name="Statut après la soutenance")
    depositDay = models.DateTimeField(auto_now_add=True,verbose_name="Date de dépôt")
    abstract = models.TextField(null=True,blank=True,verbose_name="Résumé du Mémoire")
    presentationImage = models.ImageField(upload_to = 'image_memoire/',verbose_name= "Image de présentation",null=True,blank=True)
    document = models.FileField(upload_to = "document_memoire/",verbose_name = "Document du Mémoire",validators = [FileExtensionValidator(allowed_extensions=['pdf'],message="Veuillez charger uniquement des documents de type pdf.")])
    qr_code = models.ImageField(upload_to = "qrcode/",blank = True,null=True)

    class Meta():
        verbose_name = "Mémoire"
        ordering=['-depositDay']
    
    def etudiants(self):
        students = self.etudiant_set.all()
        student_char_list = ""
        i=0
        for student in students:
            if i==0 :            
                student_char_list += str(student)
            else :
                student_char_list += " & " + str(student)
            i=i+1
        return student_char_list

    def get_list_students(self):
        return self.etudiant_set.all()

    def get_student_mat(self):
        students = self.etudiant_set.all()
        student_char_list = ""
        i=0
        for student in students:
            if i==0 :            
                student_char_list += str(student.user.username)
            else :
                student_char_list += " & " + str(student.user.username)
            i=i+1
        return student_char_list
        
    def __str__(self):
        if self.topic ==None :
            return "Mémoire non rempli"
        else:
            return self.topic
    def save(self, *args, **kwargs):
        if self.code_memoire != None :
            try :
                print("Le code est "+self.qr_code.url)
            except ValueError :
                qrcode_imag = qrcode.make(self.code_memoire)
                canvas = Image.new('RGB', (290,290), 'white')
                draw = ImageDraw.Draw(canvas)
                canvas.paste(qrcode_imag)
                fname = f'qr_code-{self.code_memoire}.png' 
                buffer = BytesIO()
                canvas.save(buffer,'PNG')
                self.qr_code.save(fname, File(buffer),save = False)
                canvas.close()
            else :
                print("Le code existe déjà !!")
        super().save(*args, **kwargs)
    def get_soutenance(self):
        soutenance = Soutenance.objects.filter(memoire = self)
        if len(soutenance) >= 1:
            return soutenance[len(soutenance)-1]
        else :
            return soutenance
        
    def checkSoutenance(self):
        soutenance = Soutenance.objects.filter(memoire = self)
        if len(soutenance) == 0:
            return False
        else :
            return True
    
    def ckeckdate(self):
        soutenance = Soutenance.objects.filter(memoire = self)
        if len(soutenance) == 0:
            return None
        else :
            soutenanceC = soutenance[len(soutenance)-1]
            currentDate = datetime.datetime.now().date()
            if currentDate >= soutenanceC.date_planned.date():
                return True
            else :
                return False


class Etudiant(models.Model):
    user = models.OneToOneField(User, default= 0, on_delete = models.CASCADE)
    last_name= models.CharField(default="", max_length=100,verbose_name="Nom")
    first_name = models.CharField(default="", max_length=100,verbose_name="Prénom") 
    avatar = models.ImageField(default = 'default.png',upload_to = 'avatar/',null=True, blank=True)   
    inscription_date = models.DateTimeField(auto_now_add=True,verbose_name="Date d'Inscription")
    memoire = models.ManyToManyField(Memoire,blank=True,verbose_name="Mémoires")    

    class Meta():
        verbose_name = "Etudiant"
    def __str__(self):
        return self.last_name + " " + self.first_name

class Soutenance(models.Model):
    memoire = models.OneToOneField(Memoire , on_delete = models.CASCADE ,verbose_name="Mémoire")
    date_planned = models.DateTimeField(verbose_name="Date de soutenance")
    jury_number = models.IntegerField(verbose_name="Numéro Jury", default=1)
    place = models.CharField(max_length=100,default="", verbose_name="Lieu de la soutenance")
    teachers = models.ManyToManyField(Enseignant,verbose_name="Enseignants assignés",through="Role")

    class Meta():
        verbose_name = "Soutenance"
    def __str__(self):
        return "Soutenance du mémoire "+ str(self.memoire)

class Role(models.Model):
    RULES_ONE = 1
    RULES_TWO = 2
    RULES_CHOICES = (
        (RULES_ONE,"Président du Jury"),
        (RULES_TWO,"Membre du Jury"),
    )

    teacher = models.ForeignKey(Enseignant, verbose_name="Enseignant",on_delete=models.CASCADE)
    soutenance = models.ForeignKey(Soutenance,on_delete=models.CASCADE)
    role = models.IntegerField (choices=RULES_CHOICES,default=RULES_TWO)

    def __str__(self):
        return str(self.teacher) + "est " + str (self.role) + str(self.soutenance) 
        

class Comment(models.Model):
    title = models.CharField(max_length=100, verbose_name= "Titre")
    content = models.TextField(verbose_name="Contenu")   
    memoire = models.ForeignKey(Memoire, on_delete= models.CASCADE,verbose_name="Mémoire")
    teacher = models.ForeignKey(Enseignant, on_delete=models.CASCADE, verbose_name="Enseignant") 
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta():
        verbose_name = "Commentaire"
    def __str__(self):
        return self.title + ' de ' + str(self.teacher)
