from django.core.management.base import BaseCommand
from dossiers.models import EtapeEvaluation

class Command(BaseCommand):
    help = 'Crée les étapes d\'évaluation selon le fichier NP exact'

    def handle(self, *args, **options):
        # Supprimer toutes les étapes existantes
        EtapeEvaluation.objects.all().delete()
        self.stdout.write("Anciennes étapes supprimées")
        
        # Créer les étapes selon le fichier NP exact
        etapes = [
            # SECTION A - VÉRIFICATION DES DOCUMENTS
            {
                'nom': 'A.1 - Diplôme original',
                'phase': 'A',
                'ordre': 1,
                'description': 'Vérification du diplôme original présenté par le candidat',
                'est_obligatoire': True
            },
            {
                'nom': 'A.2 - Traduction certifiée du diplôme',
                'phase': 'A',
                'ordre': 2,
                'description': 'Vérification de la traduction certifiée du diplôme',
                'est_obligatoire': True
            },
            {
                'nom': 'A.3 - Relevé de notes original',
                'phase': 'A',
                'ordre': 3,
                'description': 'Vérification du relevé de notes original',
                'est_obligatoire': True
            },
            {
                'nom': 'A.4 - Traduction certifiée du relevé',
                'phase': 'A',
                'ordre': 4,
                'description': 'Vérification de la traduction certifiée du relevé de notes',
                'est_obligatoire': True
            },
            {
                'nom': 'A.5 - Programme des cours',
                'phase': 'A',
                'ordre': 5,
                'description': 'Vérification du programme des cours suivi',
                'est_obligatoire': True
            },
            {
                'nom': 'A.6 - Attestation de réussite',
                'phase': 'A',
                'ordre': 6,
                'description': 'Vérification de l\'attestation de réussite',
                'est_obligatoire': True
            },
            
            # SECTION B - ANALYSE ACADÉMIQUE
            {
                'nom': 'B.1 - Niveau de formation',
                'phase': 'B',
                'ordre': 7,
                'description': 'Analyse du niveau de formation du candidat',
                'est_obligatoire': True
            },
            {
                'nom': 'B.2 - Durée des études',
                'phase': 'B',
                'ordre': 8,
                'description': 'Vérification de la durée des études effectuées',
                'est_obligatoire': True
            },
            {
                'nom': 'B.3 - Système éducatif d\'origine',
                'phase': 'B',
                'ordre': 9,
                'description': 'Analyse du système éducatif du pays d\'origine',
                'est_obligatoire': True
            },
            {
                'nom': 'B.4 - Établissement d\'origine',
                'phase': 'B',
                'ordre': 10,
                'description': 'Vérification de la reconnaissance de l\'établissement',
                'est_obligatoire': True
            },
            
            # SECTION C - ÉVALUATION DES COMPÉTENCES
            {
                'nom': 'C.1 - Compétences théoriques',
                'phase': 'C',
                'ordre': 11,
                'description': 'Évaluation des compétences théoriques acquises',
                'est_obligatoire': True
            },
            {
                'nom': 'C.2 - Compétences pratiques',
                'phase': 'C',
                'ordre': 12,
                'description': 'Évaluation des compétences pratiques',
                'est_obligatoire': True
            },
            {
                'nom': 'C.3 - Méthodologie',
                'phase': 'C',
                'ordre': 13,
                'description': 'Évaluation de la méthodologie de travail',
                'est_obligatoire': True
            },
            {
                'nom': 'C.4 - Capacité d\'analyse',
                'phase': 'C',
                'ordre': 14,
                'description': 'Évaluation de la capacité d\'analyse',
                'est_obligatoire': True
            },
            
            # SECTION D - COMPARAISON DES PROGRAMMES
            {
                'nom': 'D.1 - Correspondance des matières',
                'phase': 'D',
                'ordre': 15,
                'description': 'Comparaison des matières étudiées avec le programme local',
                'est_obligatoire': True
            },
            {
                'nom': 'D.2 - Volume horaire',
                'phase': 'D',
                'ordre': 16,
                'description': 'Comparaison du volume horaire des cours',
                'est_obligatoire': True
            },
            {
                'nom': 'D.3 - Crédits ECTS',
                'phase': 'D',
                'ordre': 17,
                'description': 'Analyse des crédits ECTS obtenus',
                'est_obligatoire': True
            },
            {
                'nom': 'D.4 - Spécialisation',
                'phase': 'D',
                'ordre': 18,
                'description': 'Analyse de la spécialisation du candidat',
                'est_obligatoire': True
            },
            
            # SECTION E - DÉCISION FINALE
            {
                'nom': 'E.1 - Score global',
                'phase': 'E',
                'ordre': 19,
                'description': 'Calcul du score global d\'équivalence',
                'est_obligatoire': True
            },
            {
                'nom': 'E.2 - Recommandation',
                'phase': 'E',
                'ordre': 20,
                'description': 'Formulation de la recommandation finale',
                'est_obligatoire': True
            },
            {
                'nom': 'E.3 - Conditions éventuelles',
                'phase': 'E',
                'ordre': 21,
                'description': 'Définition des conditions éventuelles pour l\'équivalence',
                'est_obligatoire': False
            },
        ]
        
        for etape_data in etapes:
            EtapeEvaluation.objects.create(**etape_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(etapes)} evaluation steps according to NP file')
        ) 