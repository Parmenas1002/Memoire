from django import forms
from .models import University, Ecole, Filiere,Option
from django.core.validators import FileExtensionValidator

class AddEntity(forms.Form):
    university = forms.ModelChoiceField(queryset=University.objects.all(),label="Université")
    ecole =  forms.ModelChoiceField(queryset=Ecole.objects.all())
    filiere = forms.ModelChoiceField(queryset=Filiere.objects.all(),label="Filière")
    option = forms.ModelChoiceField(queryset=Option.objects.all())


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['university'].required = True
        self.fields['ecole'].required = True
        self.fields['filiere'].required = True
        self.fields['option'].required = False

        self.fields['ecole'].queryset = Option.objects.none()
        self.fields['filiere'].queryset = Option.objects.none()
        self.fields['option'].queryset = Option.objects.none()
        
        if 'university' in self.data:
            try:
                university_id = int(self.data.get('university'))
                self.fields['ecole'].queryset = Ecole.objects.filter(university_id=university_id).order_by('name')
            except (ValueError, TypeError):
                print("error")
                pass  # invalid input from the client; ignore and fallback to empty City queryset"""
            
        if 'ecole' in self.data:
            try:
                ecole_id = int(self.data.get('ecole'))
                self.fields['filiere'].queryset = Filiere.objects.filter(entity_id=ecole_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset""
        if 'filiere' in self.data:
            try:
                filiere_id = int(self.data.get('ecole'))
                self.fields['option'].queryset = Option.objects.filter(filiere_id=filiere_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset"""

def ckeckname(name):
    if len(name)<3:
        raise forms.ValidationError('Votre nom est trop court.')
    for character in name :
        if character.isdigit() :
            raise forms.ValidationError('Votre nom est ne doit pas contenir de chiffres.')
        elif not character.isalnum():
            raise forms.ValidationError('Votre nom ne doit pas contenir des caractères spéciaux.')

class StudentRegister(forms.Form):
    name = forms.CharField(max_length=100,label="Nom")
    firstName = forms.CharField(max_length=100,label="Prénom")
    username = forms.CharField(max_length=100,label="Numéro Matricule", help_text="Votre numéro matricule sera utilisé pour la connexion")
    email = forms.EmailField(label= "Adresse Mail")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    checkPassword = forms.CharField(widget=forms.PasswordInput, label='Confirmez votre mot de passe')
    
    def clean_checkPassword(self):
        password =self.cleaned_data['password']
        check_pass = self.cleaned_data ['checkPassword']

        if len(password)<8:
            raise forms.ValidationError('Votre mot de passe est trop court.')
        if password != check_pass:
            raise forms.ValidationError('Les mots de passe ne sont pas identiques.')
    def clean_lastName(self):
        name = self.cleaned_data['lastName']
        ckeckname(name)
        return name

    def clean_firstName(self):
        fname = self.cleaned_data['firstName']
        ckeckname(fname)
        return fname
    def clean_username(self):
        matricule = self.cleaned_data['username']
        if not matricule.isdigit():
            raise forms.ValidationError('Votre numéro matricule doit etre numérique.')
        if len(matricule)!= 8:
            raise forms.ValidationError('Votre numéro matricule doit contenir huit (8) carctères.')
        return matricule


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label= 'Numéro Matricule')
    password = forms.CharField(widget=forms.PasswordInput,label ="Mot de passe")  

class LoginTForm(forms.Form):
    email = forms.EmailField(label= "Adresse Mail")
    password = forms.CharField(widget=forms.PasswordInput,label ="Mot de passe")  
    
class AddTeacher(forms.Form):
    document = forms.FileField(label="Fichier enseignant")
        
class AddAvatarForm(forms.Form):
    avatar = forms.ImageField(required=False,label="Modifier") 

def ckecknewName(name):
    for character in name :
        if character.isdigit() :
            raise forms.ValidationError('Votre nom est ne doit pas contenir de chiffres.')
        elif not character.isalnum():
            raise forms.ValidationError('Votre nom ne doit pas contenir des caractères spéciaux.')

class ModifInfo(forms.Form):
    name = forms.CharField(max_length=100,label="Nom",required=False)
    firstName = forms.CharField(max_length=100,label="Prénom",required=False)
    username = forms.CharField(max_length=100,label="Numéro Matricule",required=False)
    email = forms.EmailField(label= "Adresse Mail",required=False)

class PlandocForm(forms.Form):
    document = forms.FileField(label="Document de planification", validators=[FileExtensionValidator(allowed_extensions=['xlsx'],message="Les documents de mémoires doivent être des fichiers xlsx")])
    