from django.db import models
from comptes.models import Ecole, Academic_year

# Create your models here.

class Cloture(models.Model):
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE,verbose_name="Ecole")
    annee = models.ForeignKey(Academic_year, on_delete=models.CASCADE, verbose_name="Annee academique")
    date = models.DateField(verbose_name="Date de cloture des depots",blank=True,null=True)

    def __str__(self) :
        return "Cloture de l'école" + str(self.ecole)+ "pour l'année académique " + str(self.annee)
