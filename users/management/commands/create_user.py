from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Crée un nouvel utilisateur avec un rôle spécifique'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nom d\'utilisateur')
        parser.add_argument('email', type=str, help='Email')
        parser.add_argument('password', type=str, help='Mot de passe')
        parser.add_argument('--first-name', type=str, default='', help='Prénom')
        parser.add_argument('--last-name', type=str, default='', help='Nom de famille')
        parser.add_argument('--role', type=str, choices=['admin', 'professeur'], default='professeur', help='Rôle de l\'utilisateur')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        role = options['role']

        # Vérifier si l'utilisateur existe déjà
        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'L\'utilisateur "{username}" existe déjà')
            )
            return

        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'L\'email "{email}" est déjà utilisé')
            )
            return

        # Créer l'utilisateur
        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Utilisateur "{username}" créé avec succès avec le rôle "{role}"'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la création : {str(e)}')
            ) 