from django.db import models
from django.conf import settings
from users.models import CustomUser
from datetime import date, datetime
from django.utils import timezone

# Create your models here.

class Dossier(models.Model):
    STATUT_CHOICES = [
        ('non_traite', 'Non traité'),
        ('en_cours', 'En cours'),
        ('traite', 'Traité'),
        ('archive', 'Archivé'),
    ]
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_reception = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='non_traite')
    professeurs = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='dossiers_attribues', blank=True)

    def __str__(self):
        return self.titre

class PieceJointe(models.Model):
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='pieces_jointes')
    fichier = models.FileField(upload_to='pieces_jointes/')
    description = models.CharField(max_length=255, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fichier.name

class RapportAnalyse(models.Model):
    TYPE_RAPPORT_CHOICES = [
        ('analyse_preliminaire', 'Analyse préliminaire'),
        ('evaluation_detaille', 'Évaluation détaillée'),
        ('recommandation', 'Recommandation'),
        ('decision_finale', 'Décision finale'),
        ('autre', 'Autre'),
    ]
    
    dossier = models.OneToOneField(Dossier, on_delete=models.CASCADE, related_name='rapport')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    titre = models.CharField(max_length=255, verbose_name="Titre du rapport", default="Rapport d'analyse")
    contenu = models.TextField(verbose_name="Contenu du rapport")
    type_rapport = models.CharField(max_length=30, choices=TYPE_RAPPORT_CHOICES, default='autre', verbose_name="Type de rapport")
    date_rapport = models.DateTimeField(auto_now_add=True)
    document = models.FileField(upload_to='rapports/', blank=True, null=True, verbose_name="Document joint")

    def __str__(self):
        return f"Rapport pour {self.dossier.titre}"

class HistoriqueAction(models.Model):
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='historiques')
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    date_action = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} par {self.utilisateur} le {self.date_action}"

# Nouveaux modèles pour l'évaluation d'équivalence
class Candidat(models.Model):
    dossier = models.OneToOneField(Dossier, on_delete=models.CASCADE, related_name='candidat')
    nom = models.CharField(max_length=255)
    date_arrivee = models.DateField()
    pays_origine = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nom

class Diplome(models.Model):
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='diplomes')
    nom = models.CharField(max_length=255)
    annee = models.IntegerField()
    universite = models.CharField(max_length=255)
    pays = models.CharField(max_length=100)
    duree = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.nom} - {self.annee}"

class PieceManquante(models.Model):
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='pieces_manquantes')
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return self.description

class Competence(models.Model):
    nom = models.CharField(max_length=100)
    poids = models.IntegerField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.nom} (poids: {self.poids})"

class EvaluationCompetence(models.Model):
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='evaluations')
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE)
    note = models.IntegerField(null=True, blank=True)
    commentaires = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.competence.nom}: {self.note}/20"
    
    @property
    def points_obtenus(self):
        return (self.note * self.competence.poids) / 20

class DecisionCommission(models.Model):
    DECISION_CHOICES = [
        ('equivalence_accorder', 'Équivalence accordée'),
        ('completement_dossier', 'Complètement de dossier'),
        ('invitation_soutenance', 'Invitation soutenance'),
        ('invitation_concours', 'Invitation concours'),
        ('non_equivalent', 'Non équivalent'),
    ]
    
    candidat = models.OneToOneField(Candidat, on_delete=models.CASCADE, related_name='decision')
    score_total = models.IntegerField()
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES)
    date_decision = models.DateTimeField(auto_now_add=True)
    recommandations = models.TextField()
    commentaires = models.TextField(blank=True)
    
    @property
    def interpretation_score(self):
        if self.score_total >= 80:
            return "Excellent - Équivalence accordée recommandée"
        elif self.score_total >= 60:
            return "Bon - Complètement de dossier possible"
        elif self.score_total >= 40:
            return "Moyen - Invitation soutenance possible"
        else:
            return "Insuffisant - Non équivalent recommandé"
    
    def __str__(self):
        return f"Décision pour {self.candidat.nom}: {self.get_decision_display()}"

class StructureEvaluationGlobale(models.Model):
    """Structure globale de la fiche d'évaluation définie par l'administrateur"""
    
    # Critères obligatoires (fixes)
    sciences_geodesiques_note_max = models.IntegerField(default=16, verbose_name="Note max Sciences géodésiques")
    topographie_note_max = models.IntegerField(default=16, verbose_name="Note max Topographie")
    photogrammetrie_note_max = models.IntegerField(default=16, verbose_name="Note max Photogrammétrie")
    cartographie_note_max = models.IntegerField(default=16, verbose_name="Note max Cartographie")
    droit_foncier_note_max = models.IntegerField(default=10, verbose_name="Note max Droit foncier")
    sig_note_max = models.IntegerField(default=10, verbose_name="Note max SIG")
    teledetection_note_max = models.IntegerField(default=10, verbose_name="Note max Télédétection")
    stages_note_max = models.IntegerField(default=10, verbose_name="Note max Stages")
    
    # Critères personnalisés globaux
    criteres_personnalises_globaux = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Critères personnalisés globaux"
    )
    
    # Compétences par critère (stockées en JSON)
    competences_par_critere = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Compétences par critère"
    )
    
    # Compétences des critères fixes (stockées en JSON)
    competences_criteres_fixes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Compétences des critères fixes"
    )
    
    # Critères fixes supprimés (stockés en JSON)
    criteres_fixes_supprimes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Critères fixes supprimés"
    )
    
    # Stages configurables par l'admin (stockés en JSON)
    stages_configurables = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Stages configurables"
    )
    
    # Stages par défaut supprimés par l'admin (stockés en JSON)
    stages_defaut_supprimes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Stages par défaut supprimés"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True, verbose_name="Structure active")
    
    class Meta:
        verbose_name = "Structure d'évaluation globale"
        verbose_name_plural = "Structures d'évaluation globales"
    
    def __str__(self):
        return f"Structure d'évaluation globale (Créée le {self.date_creation.strftime('%d/%m/%Y')})"
    
    def get_structure_active():
        """Récupérer la structure active"""
        try:
            return StructureEvaluationGlobale.objects.filter(actif=True).latest('date_creation')
        except StructureEvaluationGlobale.DoesNotExist:
            # Créer une structure par défaut si aucune n'existe
            return StructureEvaluationGlobale.objects.create(
                criteres_personnalises_globaux=[],
                competences_par_critere={}
            )

# Nouveaux modèles pour l'évaluation étape par étape selon le fichier NP
class EtapeEvaluation(models.Model):
    PHASE_CHOICES = [
        ('A', 'Phase A - Vérification des documents'),
        ('B', 'Phase B - Analyse des diplômes'),
        ('C', 'Phase C - Évaluation des compétences'),
        ('D', 'Phase D - Comparaison des programmes'),
        ('E', 'Phase E - Décision finale'),
    ]
    
    nom = models.CharField(max_length=100)
    phase = models.CharField(max_length=1, choices=PHASE_CHOICES)
    ordre = models.IntegerField()
    description = models.TextField()
    est_obligatoire = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.phase} - {self.nom}"

class EvaluationEtape(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('probleme', 'Problème détecté'),
    ]
    
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='evaluations_etapes')
    etape = models.ForeignKey(EtapeEvaluation, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    note = models.IntegerField(null=True, blank=True)
    commentaires = models.TextField(blank=True)
    observations = models.TextField(blank=True)
    date_evaluation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['candidat', 'etape']
    
    def __str__(self):
        return f"{self.etape.nom} - {self.candidat.nom}: {self.get_statut_display()}"

class IndicateurDiplome(models.Model):
    """Indicateurs contenant les informations du diplôme du candidat"""
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='indicateurs_diplome')
    
    # Titre du diplôme
    titre_diplome = models.CharField(max_length=255, verbose_name="Titre du diplôme")
    description_titre = models.TextField(blank=True, verbose_name="Description du titre")
    
    # Date d'obtention
    date_obtention = models.DateField(verbose_name="Date d'obtention du diplôme")
    description_date = models.TextField(blank=True, verbose_name="Description de la date")
    
    # Pays du diplôme
    pays_diplome = models.CharField(max_length=100, verbose_name="Pays du diplôme")
    description_pays = models.TextField(blank=True, verbose_name="Description du pays")
    
    # Université ou École
    universite_ecole = models.CharField(max_length=255, verbose_name="Université ou École")
    description_etablissement = models.TextField(blank=True, verbose_name="Description de l'établissement")
    
    # Spécialité éventuelle
    specialite = models.CharField(max_length=255, blank=True, verbose_name="Spécialité éventuelle")
    description_specialite = models.TextField(blank=True, verbose_name="Description de la spécialité")
    
    # Durée de la formation
    duree_formation = models.CharField(max_length=100, verbose_name="Durée de la formation")
    description_duree = models.TextField(blank=True, verbose_name="Description de la durée")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Indicateur de diplôme"
        verbose_name_plural = "Indicateurs de diplômes"
    
    def __str__(self):
        return f"Diplôme de {self.candidat.nom} - {self.titre_diplome}"

class EtatDossier(models.Model):
    """Grille d'évaluation des dossiers pour l'évaluation d'équivalence"""
    candidat = models.OneToOneField(Candidat, on_delete=models.CASCADE, related_name='etat_dossier')
    
    # Grille d'évaluation du dossier
    est_nouveau_dossier = models.BooleanField(
        verbose_name="Nouveau dossier",
        help_text="Indique si c'est un nouveau dossier (Oui) ou un dossier déjà traité (Non)"
    )
    
    # Décisions antérieures
    a_decision_anterieure = models.BooleanField(
        default=False,
        verbose_name="A une décision antérieure"
    )
    
    date_decision_anterieure = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Date de la décision antérieure"
    )
    
    decision_anterieure = models.TextField(
        blank=True,
        verbose_name="Détails de la décision antérieure"
    )
    
    # Pièces manquantes demandées
    pieces_demandees = models.TextField(
        blank=True,
        verbose_name="Pièces complémentaires demandées"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Grille d'évaluation des dossiers"
        verbose_name_plural = "Grilles d'évaluation des dossiers"
    
    def __str__(self):
        return f"État dossier - {self.candidat.nom} ({'Nouveau' if self.est_nouveau_dossier else 'Existant'})"

class DocumentVerification(models.Model):
    TYPE_CHOICES = [
        ('diplome', 'Diplôme'),
        ('releve', 'Relevé de notes'),
        ('programme', 'Programme des cours'),
        ('traduction', 'Traduction certifiée'),
        ('attestation', 'Attestation'),
        ('autre', 'Autre'),
    ]
    
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name='documents_verifies')
    type_document = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom_document = models.CharField(max_length=255)
    est_present = models.BooleanField(default=False)
    est_valide = models.BooleanField(default=False)
    observations = models.TextField(blank=True)
    date_verification = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.nom_document}"

class ConsistanceAcademique(models.Model):
    """Consistance académique pour l'évaluation d'équivalence"""
    candidat = models.OneToOneField(Candidat, on_delete=models.CASCADE, related_name='consistance_academique')
    
    # Sciences géodésiques obligatoires (16 points)
    sciences_geodesiques_contenus = models.TextField(
        blank=True,
        verbose_name="Contenus suivis en Sciences géodésiques"
    )
    sciences_geodesiques_commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires Sciences géodésiques"
    )
    sciences_geodesiques_note = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Note Sciences géodésiques (0-16)"
    )
    
    # Checkboxes pour les compétences en Sciences géodésiques
    sciences_geodesie_geometrique = models.BooleanField(default=False, verbose_name="Géodésie géométrique")
    sciences_astronomie_geodesie_spatiale = models.BooleanField(default=False, verbose_name="Astronomie et géodésie spatiale")
    sciences_geodesie_physique = models.BooleanField(default=False, verbose_name="Géodésie physique")
    sciences_ajustements_compensations = models.BooleanField(default=False, verbose_name="Ajustements et compensations")
    sciences_systemes_referentiels = models.BooleanField(default=False, verbose_name="Systèmes et référentiels géodésiques")
    sciences_projections_cartographiques = models.BooleanField(default=False, verbose_name="Projections cartographiques")
    sciences_geodesie_appliquee = models.BooleanField(default=False, verbose_name="Géodésie appliquée")
    sciences_gnss = models.BooleanField(default=False, verbose_name="GNSS")
    sciences_micro_geodesie = models.BooleanField(default=False, verbose_name="Micro-géodésie")
    
    # Topographie obligatoire (16 points)
    topographie_contenus = models.TextField(
        blank=True,
        verbose_name="Contenus suivis en Topographie"
    )
    topographie_commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires Topographie"
    )
    topographie_note = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Note Topographie (0-16)"
    )
    
    # Checkboxes pour les compétences en Topographie
    topographie_theorique_pratique = models.BooleanField(default=False, verbose_name="Théorique et pratique")
    topographie_topometrique_instrumentation = models.BooleanField(default=False, verbose_name="Topométrique et instrumentation")
    topographie_techniques_mensuration = models.BooleanField(default=False, verbose_name="Techniques de mensuration")
    
    # Photogrammétrie obligatoire (16 points)
    photogrammetrie_contenus = models.TextField(
        blank=True,
        verbose_name="Contenus suivis en Photogrammétrie"
    )
    photogrammetrie_commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires Photogrammétrie"
    )
    photogrammetrie_note = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Note Photogrammétrie (0-16)"
    )
    
    # Checkboxes pour les compétences en Photogrammétrie
    photogrammetrie_base_approfondie = models.BooleanField(default=False, verbose_name="Base et approfondie")
    photogrammetrie_photographies_aeriennes = models.BooleanField(default=False, verbose_name="Mise en place des photographies aériennes")
    photogrammetrie_aerotriangulation = models.BooleanField(default=False, verbose_name="Aérotriangulation")
    photogrammetrie_restitution = models.BooleanField(default=False, verbose_name="Restitution photogrammétrique")
    photogrammetrie_produits_derives = models.BooleanField(default=False, verbose_name="Génération de produits dérivés (MNT/Ortho)")
    photogrammetrie_drone = models.BooleanField(default=False, verbose_name="Drone")
    
    # Cartographie obligatoire (16 points)
    cartographie_contenus = models.TextField(
        blank=True,
        verbose_name="Contenus suivis en Cartographie"
    )
    cartographie_commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires Cartographie"
    )
    cartographie_note = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Note Cartographie (0-16)"
    )
    
    # Checkboxes pour les compétences en Cartographie
    cartographie_topographique = models.BooleanField(default=False, verbose_name="Cartographie topographique")
    cartographie_representation_cartographique = models.BooleanField(default=False, verbose_name="Systèmes de représentation cartographique")
    cartographie_thematique = models.BooleanField(default=False, verbose_name="Cartographie thématique")
    cartographie_semiologie_langage = models.BooleanField(default=False, verbose_name="Sémiologie et langage cartographique")
    cartographie_dao_cao = models.BooleanField(default=False, verbose_name="DAO/CAO")
    cartographie_drone = models.BooleanField(default=False, verbose_name="Drone (Cartographie)")
    
    # Critères personnalisés ajoutés par le professeur
    # Chaque critère : {id, nom, note_max, note, contenus, commentaires, competences:[], competences_cochees:[]}
    criteres_personnalises = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Critères personnalisés"
    )
    
    # Droit foncier, cadastre et aménagements fonciers obligatoires (10 points)
    droit_foncier_contenus = models.TextField(
        blank=True,
        verbose_name="Contenus suivis en Droit foncier"
    )
    droit_foncier_commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires Droit foncier"
    )
    droit_foncier_note = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Note Droit foncier (0-10)"
    )
    
    # Checkboxes pour les compétences en Droit foncier
    droit_foncier_droit = models.BooleanField(default=False, verbose_name="Droit foncier")
    droit_foncier_techniques_cadastrales = models.BooleanField(default=False, verbose_name="Techniques cadastrales")
    droit_foncier_gestion_amenagement = models.BooleanField(default=False, verbose_name="Gestion foncière et aménagement")
    droit_foncier_reglementations = models.BooleanField(default=False, verbose_name="Réglementations cadastre et propriété")
    
    # Systèmes d'Information Géographique (SIG) (10 points)
    sig_contenus = models.TextField(
        blank=True,
        verbose_name="Contenus suivis en SIG"
    )
    sig_commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires SIG"
    )
    sig_note = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Note SIG (0-10)"
    )
    
    # Checkboxes pour les compétences en SIG
    sig_bases = models.BooleanField(default=False, verbose_name="Bases en SIG")
    sig_gestion_analyse_donnees = models.BooleanField(default=False, verbose_name="Gestion et analyse des données spatiales")
    sig_bases_donnees_geographiques = models.BooleanField(default=False, verbose_name="Bases de données géographiques")
    sig_web_mapping = models.BooleanField(default=False, verbose_name="Web mapping")
    
    # Télédétection (10 points)
    teledetection_contenus = models.TextField(
        blank=True,
        verbose_name="Contenus suivis en Télédétection"
    )
    teledetection_commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires Télédétection"
    )
    teledetection_note = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Note Télédétection (0-10)"
    )
    
    # Checkboxes pour les compétences en Télédétection
    teledetection_bases_physiques = models.BooleanField(default=False, verbose_name="Bases physiques de la télédétection")
    teledetection_traitement_images = models.BooleanField(default=False, verbose_name="Traitement d'images optique/radar")
    teledetection_applications = models.BooleanField(default=False, verbose_name="Applications de la télédétection")
    
    # Stages et professionnalisation (10 points)
    stages_contenus = models.TextField(
        blank=True,
        verbose_name="Contenus des stages effectués"
    )
    stages_commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires sur les stages"
    )
    stages_note = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Note Stages (0-10)"
    )
    
    # Stages configurables par l'admin (stockés en JSON)
    stages_configurables = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Stages configurables"
    )
    
    # Stages et professionnalisation
    stage_conservation_fonciere = models.BooleanField(
        default=False,
        verbose_name="Stage conservation foncière ANCFCC (1 semaine)"
    )
    stage_cadastre = models.BooleanField(
        default=False,
        verbose_name="Stage cadastre ANCFCC (2 semaines)"
    )
    stage_geodesie = models.BooleanField(
        default=False,
        verbose_name="Stage de Géodésie (2 semaines)"
    )
    stage_topographie = models.BooleanField(
        default=False,
        verbose_name="Stage de Topographie (2 semaines)"
    )
    stage_photogrammetrie = models.BooleanField(
        default=False,
        verbose_name="Stage de Photogrammétrie (2 semaines)"
    )
    
    # Stages configurables cochés par le professeur (stockés en JSON)
    stages_configurables_cochees = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Stages configurables cochés"
    )
    
    # État des stages (nouveaux champs pour les boutons)
    stages_acheves = models.BooleanField(
        default=False,
        verbose_name="Stages achevés"
    )
    stages_non_acheves = models.BooleanField(
        default=False,
        verbose_name="Stages non achevés"
    )
    message_stages_non_acheves = models.TextField(
        blank=True,
        verbose_name="Message pour stages non achevés"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Consistance académique"
        verbose_name_plural = "Consistances académiques"
    
    def __str__(self):
        return f"Consistance académique - {self.candidat.nom}"
    
    @property
    def note_totale(self):
        """Calcule la note totale de la consistance académique"""
        notes = []
        
        # Fonction helper pour convertir en nombre
        def to_float(value):
            if value is None:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        # Sciences géodésiques (16 points)
        if self.sciences_geodesiques_note is not None:
            note = to_float(self.sciences_geodesiques_note)
            if note is not None:
                notes.append(note)
        
        # Topographie (16 points)
        if self.topographie_note is not None:
            note = to_float(self.topographie_note)
            if note is not None:
                notes.append(note)
        
        # Photogrammétrie (16 points)
        if self.photogrammetrie_note is not None:
            note = to_float(self.photogrammetrie_note)
            if note is not None:
                notes.append(note)
        
        # Cartographie (16 points)
        if self.cartographie_note is not None:
            note = to_float(self.cartographie_note)
            if note is not None:
                notes.append(note)
        
        # Droit foncier (10 points)
        if self.droit_foncier_note is not None:
            note = to_float(self.droit_foncier_note)
            if note is not None:
                notes.append(note)
        
        # SIG (10 points)
        if self.sig_note is not None:
            note = to_float(self.sig_note)
            if note is not None:
                notes.append(note)
        
        # Télédétection (10 points)
        if self.teledetection_note is not None:
            note = to_float(self.teledetection_note)
            if note is not None:
                notes.append(note)
        
        # Stages (10 points)
        if self.stages_note is not None:
            note = to_float(self.stages_note)
            if note is not None:
                notes.append(note)
        
        # Critères personnalisés ajoutés par le professeur
        for critere in self.criteres_personnalises:
            if critere.get('note') is not None:
                note = to_float(critere.get('note'))
                if note is not None:
                    notes.append(note)
        
        return sum(notes) if notes else 0
    
    def evaluer_criteres_obligatoires(self):
        """
        Évalue les critères obligatoires selon la règle :
        - Note < 50% de la note allouée = critère non acquis
        - Si un critère obligatoire est non acquis = dossier insuffisant
        """
        criteres_evaluation = {}
        criteres_non_acquis = []
        
        # Fonction helper pour convertir en nombre
        def to_float(value):
            if value is None:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        # Sciences géodésiques obligatoires (16 points)
        if self.sciences_geodesiques_note is not None:
            note = to_float(self.sciences_geodesiques_note)
            if note is not None:
                note_min = 16 * 0.5  # 50% de 16 = 8
                if note < note_min:
                    criteres_evaluation['sciences_geodesiques'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 16,
                        'acquis': False,
                        'pourcentage': (note / 16) * 100,
                        'personnalise': False
                    }
                    criteres_non_acquis.append('Sciences géodésiques')
                else:
                    criteres_evaluation['sciences_geodesiques'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 16,
                        'acquis': True,
                        'pourcentage': (note / 16) * 100,
                        'personnalise': False
                    }
        
        # Topographie obligatoire (16 points)
        if self.topographie_note is not None:
            note = to_float(self.topographie_note)
            if note is not None:
                note_min = 16 * 0.5  # 50% de 16 = 8
                if note < note_min:
                    criteres_evaluation['topographie'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 16,
                        'acquis': False,
                        'pourcentage': (note / 16) * 100,
                        'personnalise': False
                    }
                    criteres_non_acquis.append('Topographie')
                else:
                    criteres_evaluation['topographie'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 16,
                        'acquis': True,
                        'pourcentage': (note / 16) * 100,
                        'personnalise': False
                    }
        
        # Photogrammétrie obligatoire (16 points)
        if self.photogrammetrie_note is not None:
            note = to_float(self.photogrammetrie_note)
            if note is not None:
                note_min = 16 * 0.5  # 50% de 16 = 8
                if note < note_min:
                    criteres_evaluation['photogrammetrie'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 16,
                        'acquis': False,
                        'pourcentage': (note / 16) * 100,
                        'personnalise': False
                    }
                    criteres_non_acquis.append('Photogrammétrie')
                else:
                    criteres_evaluation['photogrammetrie'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 16,
                        'acquis': True,
                        'pourcentage': (note / 16) * 100,
                        'personnalise': False
                    }
        
        # Cartographie obligatoire (16 points)
        if self.cartographie_note is not None:
            note = to_float(self.cartographie_note)
            if note is not None:
                note_min = 16 * 0.5  # 50% de 16 = 8
                if note < note_min:
                    criteres_evaluation['cartographie'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 16,
                        'acquis': False,
                        'pourcentage': (note / 16) * 100,
                        'personnalise': False
                    }
                    criteres_non_acquis.append('Cartographie')
                else:
                    criteres_evaluation['cartographie'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 16,
                        'acquis': True,
                        'pourcentage': (note / 16) * 100,
                        'personnalise': False
                    }
        
        # Droit foncier obligatoire (10 points)
        if self.droit_foncier_note is not None:
            note = to_float(self.droit_foncier_note)
            if note is not None:
                note_min = 10 * 0.5  # 50% de 10 = 5
                if note < note_min:
                    criteres_evaluation['droit_foncier'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 10,
                        'acquis': False,
                        'pourcentage': (note / 10) * 100,
                        'personnalise': False
                    }
                    criteres_non_acquis.append('Droit foncier')
                else:
                    criteres_evaluation['droit_foncier'] = {
                        'note': note,
                        'note_min': note_min,
                        'note_max': 10,
                        'acquis': True,
                        'pourcentage': (note / 10) * 100,
                        'personnalise': False
                    }
        
        # SIG (10 points) - NON OBLIGATOIRE
        if self.sig_note is not None:
            note = to_float(self.sig_note)
            if note is not None:
                criteres_evaluation['sig'] = {
                    'note': note,
                    'note_min': 0,  # Pas de minimum pour les critères non-obligatoires
                    'note_max': 10,
                    'acquis': True,  # Toujours considéré comme acquis
                    'pourcentage': (note / 10) * 100,
                    'personnalise': False
                }
        
        # Télédétection (10 points) - NON OBLIGATOIRE
        if self.teledetection_note is not None:
            note = to_float(self.teledetection_note)
            if note is not None:
                criteres_evaluation['teledetection'] = {
                    'note': note,
                    'note_min': 0,  # Pas de minimum pour les critères non-obligatoires
                    'note_max': 10,
                    'acquis': True,  # Toujours considéré comme acquis
                    'pourcentage': (note / 10) * 100,
                    'personnalise': False
                }
        
        # Stages (10 points) - NON OBLIGATOIRE
        if self.stages_note is not None:
            note = to_float(self.stages_note)
            if note is not None:
                criteres_evaluation['stages'] = {
                    'note': note,
                    'note_min': 0,  # Pas de minimum pour les critères non-obligatoires
                    'note_max': 10,
                    'acquis': True,  # Toujours considéré comme acquis
                    'pourcentage': (note / 10) * 100,
                    'personnalise': False
                }
        
        # Critères personnalisés ajoutés par le professeur - NON OBLIGATOIRES
        for critere in self.criteres_personnalises:
            if critere.get('note') is not None:
                note_max = to_float(critere.get('note_max', 10))
                note_actuelle = to_float(critere.get('note', 0))
                
                if note_max is not None and note_actuelle is not None:
                    criteres_evaluation[f"critere_personnalise_{critere.get('id')}"] = {
                        'note': note_actuelle,
                        'note_min': 0,  # Pas de minimum pour les critères non-obligatoires
                        'note_max': note_max,
                        'acquis': True,  # Toujours considéré comme acquis
                        'pourcentage': (note_actuelle / note_max) * 100,
                        'nom': critere.get('nom', 'Critère personnalisé'),
                        'personnalise': True
                    }
        
        return {
            'criteres': criteres_evaluation,
            'criteres_non_acquis': criteres_non_acquis,
            'dossier_suffisant': len(criteres_non_acquis) == 0,
            'total_criteres_evalues': len(criteres_evaluation)
        }
    
    def interpreter_resultats_globaux(self):
        """
        Interprète les résultats globaux selon les nouvelles règles STRICTES :
        - 76 à 100 points : formation validée avec excellence (SEULEMENT si tous les critères obligatoires sont acquis)
        - 50 à 75 points : formation solide, équivalence recommandée sous conditions (SEULEMENT si tous les critères obligatoires sont acquis)
        - Moins de 50 points : Formation insuffisante
        - Si un critère obligatoire < 50% : Formation insuffisante (même avec 76-100 points)
        """
        note_totale = self.note_totale
        
        # Vérifier d'abord les critères obligatoires
        evaluation_obligatoires = self.evaluer_criteres_obligatoires()
        criteres_non_acquis = evaluation_obligatoires['criteres_non_acquis']
        
        # Si un critère obligatoire n'est pas acquis, le dossier est automatiquement insuffisant
        if criteres_non_acquis:
            criteres_liste = ", ".join(criteres_non_acquis)
            return {
                'niveau': 'insuffisant_obligatoire',
                'titre': 'Formation insuffisante - Critères obligatoires non acquis',
                'description': f'Formation insuffisante pour l\'octroi de l\'équivalence. Critères obligatoires non acquis : {criteres_liste}. Le dossier du candidat est jugé insuffisant même avec un score total de {note_totale}/100.',
                'couleur': 'danger',
                'icone': 'fas fa-exclamation-triangle',
                'note_totale': note_totale,
                'note_max': 100,
                'criteres_non_acquis': criteres_non_acquis
            }
        
        # Si tous les critères obligatoires sont acquis, on peut évaluer selon le score total
        if note_totale >= 76:
            return {
                'niveau': 'excellence',
                'titre': 'Formation validée avec excellence',
                'description': 'Formation parfaitement en adéquation avec les exigences du diplôme d\'ingénieur topographe de l\'IAV Hassan II avec possibilité d\'exiger les stages complémentaires.',
                'couleur': 'success',
                'icone': 'fas fa-star',
                'note_totale': note_totale,
                'note_max': 100
            }
        elif note_totale >= 50:
            return {
                'niveau': 'solide',
                'titre': 'Formation solide',
                'description': 'Équivalence recommandée sous conditions des améliorations sous forme de formations complémentaires et de stages.',
                'couleur': 'warning',
                'icone': 'fas fa-check-circle',
                'note_totale': note_totale,
                'note_max': 100
            }
        else:
            return {
                'niveau': 'insuffisant',
                'titre': 'Formation insuffisante',
                'description': 'Formation insuffisante pour obtenir l\'équivalence. Formation Académique diplômante obligatoire.',
                'couleur': 'danger',
                'icone': 'fas fa-times-circle',
                'note_totale': note_totale,
                'note_max': 100
            }

class Notification(models.Model):
    TYPES = [
        ('affectation', 'Affectation de dossier'),
        ('traitement', 'Traitement terminé'),
        ('evaluation', 'Nouvelle évaluation'),
        ('system', 'Notification système'),
        ('retour', 'Retour à l\'admin'),
        ('renvoi', 'Renvoyer au professeur'),
    ]
    
    destinataire = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=20, choices=TYPES)
    titre = models.CharField(max_length=255)
    message = models.TextField()
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.destinataire.username}"

class DossierTraite(models.Model):
    """Modèle pour les dossiers déjà traités avec historique complet"""
    
    # Choix pour les pays
    PAYS_CHOICES = [
        ('maroc', 'Maroc'),
        ('algerie', 'Algérie'),
        ('tunisie', 'Tunisie'),
        ('libye', 'Libye'),
        ('egypte', 'Égypte'),
        ('mauritanie', 'Mauritanie'),
        ('mali', 'Mali'),
        ('niger', 'Niger'),
        ('tchad', 'Tchad'),
        ('soudan', 'Soudan'),
        ('ethiopie', 'Éthiopie'),
        ('somalie', 'Somalie'),
        ('djibouti', 'Djibouti'),
        ('erythree', 'Érythrée'),
        ('kenya', 'Kenya'),
        ('ouganda', 'Ouganda'),
        ('tanzanie', 'Tanzanie'),
        ('rwanda', 'Rwanda'),
        ('burundi', 'Burundi'),
        ('rdc', 'République démocratique du Congo'),
        ('congo', 'République du Congo'),
        ('gabon', 'Gabon'),
        ('guinee_equatoriale', 'Guinée équatoriale'),
        ('cameroun', 'Cameroun'),
        ('tchad', 'Tchad'),
        ('republique_centrafricaine', 'République centrafricaine'),
        ('soudan_du_sud', 'Soudan du Sud'),
        ('nigeria', 'Nigeria'),
        ('benin', 'Bénin'),
        ('togo', 'Togo'),
        ('ghana', 'Ghana'),
        ('cote_ivoire', 'Côte d\'Ivoire'),
        ('liberia', 'Libéria'),
        ('sierra_leone', 'Sierra Leone'),
        ('guinee', 'Guinée'),
        ('guinee_bissau', 'Guinée-Bissau'),
        ('gambie', 'Gambie'),
        ('senegal', 'Sénégal'),
        ('cap_vert', 'Cap-Vert'),
        ('maurice', 'Maurice'),
        ('seychelles', 'Seychelles'),
        ('madagascar', 'Madagascar'),
        ('comores', 'Comores'),
        ('france', 'France'),
        ('belgique', 'Belgique'),
        ('suisse', 'Suisse'),
        ('canada', 'Canada'),
        ('allemagne', 'Allemagne'),
        ('italie', 'Italie'),
        ('espagne', 'Espagne'),
        ('portugal', 'Portugal'),
        ('pays_bas', 'Pays-Bas'),
        ('royaume_uni', 'Royaume-Uni'),
        ('etats_unis', 'États-Unis'),
        ('bresil', 'Brésil'),
        ('argentine', 'Argentine'),
        ('chili', 'Chili'),
        ('perou', 'Pérou'),
        ('colombie', 'Colombie'),
        ('venezuela', 'Venezuela'),
        ('mexique', 'Mexique'),
        ('chine', 'Chine'),
        ('japon', 'Japon'),
        ('coree_du_sud', 'Corée du Sud'),
        ('inde', 'Inde'),
        ('pakistan', 'Pakistan'),
        ('bangladesh', 'Bangladesh'),
        ('sri_lanka', 'Sri Lanka'),
        ('thailande', 'Thaïlande'),
        ('vietnam', 'Vietnam'),
        ('malaisie', 'Malaisie'),
        ('singapour', 'Singapour'),
        ('indonesie', 'Indonésie'),
        ('philippines', 'Philippines'),
        ('australie', 'Australie'),
        ('nouvelle_zelande', 'Nouvelle-Zélande'),
        ('russie', 'Russie'),
        ('ukraine', 'Ukraine'),
        ('pologne', 'Pologne'),
        ('republique_tcheque', 'République tchèque'),
        ('slovaquie', 'Slovaquie'),
        ('hongrie', 'Hongrie'),
        ('roumanie', 'Roumanie'),
        ('bulgarie', 'Bulgarie'),
        ('grece', 'Grèce'),
        ('turquie', 'Turquie'),
        ('israel', 'Israël'),
        ('liban', 'Liban'),
        ('jordanie', 'Jordanie'),
        ('syrie', 'Syrie'),
        ('irak', 'Irak'),
        ('iran', 'Iran'),
        ('arabie_saoudite', 'Arabie saoudite'),
        ('koweit', 'Koweït'),
        ('qatar', 'Qatar'),
        ('emirats_arabes_unis', 'Émirats arabes unis'),
        ('oman', 'Oman'),
        ('yemen', 'Yémen'),
        ('afghanistan', 'Afghanistan'),
        ('autre', 'Autre'),
    ]
    
    # Choix pour les universités (principales universités marocaines et internationales)
    UNIVERSITE_CHOICES = [
        # Universités marocaines principales
        ('iav_hassan_ii', 'IAV Hassan II - Institut Agronomique et Vétérinaire Hassan II'),
        ('universite_mohammed_v', 'Université Mohammed V de Rabat'),
        ('universite_mohammed_vi', 'Université Mohammed VI Polytechnique'),
        ('universite_cadi_ayyad', 'Université Cadi Ayyad de Marrakech'),
        ('universite_sidi_mohammed', 'Université Sidi Mohammed Ben Abdellah de Fès'),
        ('universite_moulay_ismail', 'Université Moulay Ismail de Meknès'),
        ('universite_ibn_zohr', 'Université Ibn Zohr d\'Agadir'),
        ('universite_ibn_tofail', 'Université Ibn Tofail de Kénitra'),
        ('universite_ibn_khaldoun', 'Université Ibn Khaldoun de Tiaret'),
        ('universite_ibn_sina', 'Université Ibn Sina de Marrakech'),
        ('universite_ibn_rochd', 'Université Ibn Rochd de Casablanca'),
        ('universite_ibn_ghazi', 'Université Ibn Ghazi de Meknès'),
        ('universite_ibn_al_haitham', 'Université Ibn Al Haitham de Marrakech'),
        ('universite_ibn_al_aziz', 'Université Ibn Al Aziz de Tétouan'),
        ('universite_ibn_al_arabi', 'Université Ibn Al Arabi de Tétouan'),
        ('universite_ibn_al_quayyim', 'Université Ibn Al Quayyim de Tétouan'),
        
        # Universités internationales principales
        ('sorbonne', 'Sorbonne Université (France)'),
        ('paris_saclay', 'Université Paris-Saclay (France)'),
        ('polytechnique', 'École Polytechnique (France)'),
        ('ens_paris', 'École Normale Supérieure de Paris (France)'),
        ('ecole_centrale', 'École Centrale Paris (France)'),
        ('mines_paris', 'École des Mines de Paris (France)'),
        ('ponts_paris', 'École des Ponts ParisTech (France)'),
        ('ucl', 'University College London (Royaume-Uni)'),
        ('imperial_college', 'Imperial College London (Royaume-Uni)'),
        ('oxford', 'University of Oxford (Royaume-Uni)'),
        ('cambridge', 'University of Cambridge (Royaume-Uni)'),
        ('mit', 'Massachusetts Institute of Technology (États-Unis)'),
        ('stanford', 'Stanford University (États-Unis)'),
        ('harvard', 'Harvard University (États-Unis)'),
        ('berkeley', 'University of California Berkeley (États-Unis)'),
        ('caltech', 'California Institute of Technology (États-Unis)'),
        ('eth_zurich', 'ETH Zurich (Suisse)'),
        ('epfl', 'École Polytechnique Fédérale de Lausanne (Suisse)'),
        ('tu_munich', 'Technical University of Munich (Allemagne)'),
        ('rwth_aachen', 'RWTH Aachen University (Allemagne)'),
        ('tu_berlin', 'Technical University of Berlin (Allemagne)'),
        ('politecnico_milano', 'Politecnico di Milano (Italie)'),
        ('politecnico_torino', 'Politecnico di Torino (Italie)'),
        ('upc_barcelona', 'Universitat Politècnica de Catalunya (Espagne)'),
        ('upm_madrid', 'Universidad Politécnica de Madrid (Espagne)'),
        ('tu_delft', 'Delft University of Technology (Pays-Bas)'),
        ('kth_stockholm', 'KTH Royal Institute of Technology (Suède)'),
        ('dtu_copenhagen', 'Technical University of Denmark (Danemark)'),
        ('ntnu_trondheim', 'Norwegian University of Science and Technology (Norvège)'),
        ('aalto_helsinki', 'Aalto University (Finlande)'),
        ('chalmers_gothenburg', 'Chalmers University of Technology (Suède)'),
        ('autre', 'Autre université'),
    ]
    
    # Informations de base
    numero = models.CharField(max_length=50, unique=True, verbose_name="Numéro")
    demandeur_candidat = models.CharField(max_length=200, verbose_name="Demandeur/Candidat")
    reference = models.CharField(max_length=100, verbose_name="Référence")
    date_envoi = models.DateField(verbose_name="Date d'envoi")
    
    # Informations de réception
    reference_reception = models.CharField(max_length=100, blank=True, verbose_name="Référence de réception")
    date_reception = models.DateField(verbose_name="Date de réception")
    
    # Informations académiques
    diplome = models.CharField(max_length=200, verbose_name="Diplôme")
    universite = models.CharField(max_length=50, choices=UNIVERSITE_CHOICES, verbose_name="Université")
    universite_autre = models.CharField(max_length=200, blank=True, verbose_name="Autre université (si applicable)")
    pays = models.CharField(max_length=50, choices=PAYS_CHOICES, verbose_name="Pays")
    pays_autre = models.CharField(max_length=100, blank=True, verbose_name="Autre pays (si applicable)")
    
    # Informations de décision
    date_avis = models.DateField(null=True, blank=True, verbose_name="Date de l'avis")
    avis_commission = models.TextField(verbose_name="Avis de la commission")
    date_decision = models.DateField(null=True, blank=True, verbose_name="Date de décision")
    
    # Historique des réunions
    reunions = models.JSONField(default=list, blank=True, verbose_name="Réunions")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Créé par"
    )
    
    class Meta:
        verbose_name = "Dossier traité"
        verbose_name_plural = "Dossiers traités"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Dossier {self.numero} - {self.demandeur_candidat}"
    
    def get_universite_display(self):
        """Retourne le nom complet de l'université"""
        if self.universite == 'autre' and self.universite_autre:
            return self.universite_autre
        
        # Obtenir le nom complet depuis les choix
        for choice_value, choice_label in self.UNIVERSITE_CHOICES:
            if choice_value == self.universite:
                return choice_label
        return self.universite
    
    def get_pays_display(self):
        """Retourne le nom complet du pays"""
        if self.pays == 'autre' and self.pays_autre:
            return self.pays_autre
        
        # Obtenir le nom complet depuis les choix
        for choice_value, choice_label in self.PAYS_CHOICES:
            if choice_value == self.pays:
                return choice_label
        return self.pays
    
    def ajouter_reunion(self, date_reunion, participants, ordre_du_jour, decisions):
        """Ajoute une nouvelle réunion à l'historique"""
        reunion = {
            'id': len(self.reunions) + 1,
            'date': date_reunion.strftime('%Y-%m-%d'),
            'participants': participants,
            'ordre_du_jour': ordre_du_jour,
            'decisions': decisions,
            'date_ajout': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.reunions.append(reunion)
        self.save()
        return reunion
    
    def get_derniere_reunion(self):
        """Retourne la dernière réunion"""
        if self.reunions:
            return self.reunions[-1]
        return None
    
    def get_nombre_reunions(self):
        """Retourne le nombre total de réunions"""
        return len(self.reunions)
