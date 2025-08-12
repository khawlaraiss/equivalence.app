from django.core.management.base import BaseCommand
from dossiers.models import Competence

class Command(BaseCommand):
    help = 'Crée les compétences par défaut pour l\'évaluation d\'équivalence'

    def handle(self, *args, **options):
        competences_defaut = [
            {
                'nom': 'Mathématiques',
                'description': 'Compétences en mathématiques fondamentales et appliquées',
                'poids': 20
            },
            {
                'nom': 'Physique',
                'description': 'Connaissances en physique générale et mécanique',
                'poids': 15
            },
            {
                'nom': 'Topographie',
                'description': 'Compétences en topographie et levés',
                'poids': 25
            },
            {
                'nom': 'Géodésie',
                'description': 'Connaissances en géodésie et systèmes de référence',
                'poids': 20
            },
            {
                'nom': 'Cartographie',
                'description': 'Compétences en cartographie et SIG',
                'poids': 10
            },
            {
                'nom': 'Informatique',
                'description': 'Maîtrise des outils informatiques et logiciels spécialisés',
                'poids': 10
            }
        ]

        for comp_data in competences_defaut:
            competence, created = Competence.objects.get_or_create(
                nom=comp_data['nom'],
                defaults={
                    'description': comp_data['description'],
                    'poids': comp_data['poids']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Compétence créée: {competence.nom}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Compétence existante: {competence.nom}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Total: {Competence.objects.count()} compétences disponibles')
        ) 