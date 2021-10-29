from django.core.exceptions import ValidationError

def validate_file_size(value):
    filesize = value.size
    if filesize > 5000000:
        raise ValidationError("La taille de votre fichier dépasse les 5Mo")
    else:
        return value