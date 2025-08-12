from django.core.management.base import BaseCommand
from dossiers.models import Competence

class Command(BaseCommand):
    help = 'Initialise les compétences par défaut pour l\'évaluation d\'équivalence'

    def handle(self, *args, **options):
        competences_data = [
            {
                'nom': 'Sciences géodésiques',
                'poids': 16,
                'description': 'Géodésie géométrique, géodésie physique, ajustements moindres carrés'
            },
            {
                'nom': 'Topographie',
                'poids': 16,
                'description': 'Topométrie, nivellement, tachéométrie'
            },
            {
                'nom': 'Photogrammétrie',
                'poids': 16,
                'description': 'Aérophotogrammétrie, drone'
            },
            {
                'nom': 'Cartographie',
                'poids': 16,
                'description': 'Cartographie numérique, représentation 2D/3D'
            },
            {
                'nom': 'SIG et télédétection',
                'poids': 16,
                'description': 'Imagerie satellite, orthoimage, analyse spatiale'
            },
            {
                'nom': 'Droit foncier et langue',
                'poids': 4,
                'description': 'Droit foncier, langue française/scientifique'
            }
        ]

        for comp_data in competences_data:
            competence, created = Competence.objects.get_or_create(
                nom=comp_data['nom'],
                defaults={
                    'poids': comp_data['poids'],
                    'description': comp_data['description']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Compétence créée : {competence.nom}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Compétence déjà existante : {competence.nom}')
                )

        self.stdout.write(
            self.style.SUCCESS('Initialisation des compétences terminée !')
        ) 