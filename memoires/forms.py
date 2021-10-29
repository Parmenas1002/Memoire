from django import forms
from .validators import validate_file_size
from django.core.validators import FileExtensionValidator
from comptes.forms import AddEntity
from comptes.models import Memoire

class EndOne(forms.Form):
    topic =forms.CharField(max_length=220,label="Thème du mémoire") 
    supervisor = forms.CharField(max_length=120,label="Superviseur du Mémoire")
    document = forms.FileField(label="Document du Mémoire", validators=[FileExtensionValidator(allowed_extensions=['pdf'],message="Les documents de mémoires doivent être des fichiers pdf"),validate_file_size])

class EndTwo(EndOne):
    patnerUsername = forms.CharField(max_length=100,label="Binôme" )
    patnerPassword = forms.CharField(widget=forms.PasswordInput,label="Mot de passe de votre binôme")

class DepositOne(AddEntity):
    topic =forms.CharField(max_length=220,label="Thème du mémoire") 
    supervisor = forms.CharField(max_length=120,label="Superviseur du Mémoire")
    document = forms.FileField(label="Document du Mémoire", validators=[FileExtensionValidator(allowed_extensions=['pdf'],message="Les documents de mémoires doivent être des fichiers pdf"),validate_file_size])

class DepositTwo(DepositOne):
    patnerUsername = forms.CharField(max_length=100,label="Matricule de votre Binôme" )
    patnerPassword = forms.CharField(widget=forms.PasswordInput,label="Mot de passe de votre binôme")

class ModifyDocument(forms.Form):
    document = forms.FileField(label="Document du Mémoire", validators=[FileExtensionValidator(allowed_extensions=['pdf'],message="Les documents de mémoires doivent être des fichiers pdf"),validate_file_size])

class AddTInfo(forms.ModelForm):
    class Meta:
        model = Memoire
        fields = ['middleClass','mention']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['middleClass'].required = True
        self.fields['mention'].required = True

class AddComment(forms.Form):
    title = forms.CharField(max_length=220, label="Titre")
    content = forms.CharField(widget= forms.Textarea, label='Contenu du commentaire')

class StudentModifForm(forms.Form):
    presentationImage = forms.ImageField(label= "Image de présentation")
    abstract = forms.CharField(widget= forms.Textarea, label='Résumé du mémoire')