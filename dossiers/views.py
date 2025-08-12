from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from .models import Dossier, PieceJointe, RapportAnalyse, HistoriqueAction, Candidat, Diplome, PieceManquante, Competence, EvaluationCompetence, DecisionCommission, Notification, EtapeEvaluation, EvaluationEtape, IndicateurDiplome, EtatDossier, ConsistanceAcademique, DossierTraite, StructureEvaluationGlobale
from users.models import CustomUser
from django.db import models
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import FileResponse
import os
from django.conf import settings
import pandas as pd

def evaluer_candidat(candidat_id):
    """
    Fonction pour évaluer un candidat selon la grille d'équivalence
    """
    candidat = Candidat.objects.get(id=candidat_id)
    
    # Calculer le score total
    evaluations = candidat.evaluations.all()
    score_total = sum(eval.points_obtenus for eval in evaluations)
    
    # Déterminer la décision selon les seuils
    if score_total >= 76:
        decision = 'equivalence_accorder'
    elif score_total >= 50:
        decision = 'completement_dossier'
    elif score_total >= 30:
        decision = 'invitation_soutenance'
    elif score_total >= 20:
        decision = 'invitation_concours'
    else:
        decision = 'non_equivalent'
    
    # Générer les recommandations selon la décision
    recommandations = generer_recommandations(candidat, decision, score_total)
    
    # Créer ou mettre à jour la décision
    decision_obj, created = DecisionCommission.objects.get_or_create(
        candidat=candidat,
        defaults={
            'score_total': score_total,
            'decision': decision,
            'recommandations': recommandations
        }
    )
    
    if not created:
        decision_obj.score_total = score_total
        decision_obj.decision = decision
        decision_obj.recommandations = recommandations
        decision_obj.save()
    
    return decision_obj

def generer_recommandations(candidat, decision, score_total):
    """
    Génère les recommandations selon la décision et le score
    """
    recommandations = []
    
    if decision == 'equivalence_accorder':
        recommandations.append("✅ Équivalence accordée")
        recommandations.append("📋 Aucune condition supplémentaire requise")
    
    elif decision == 'completement_dossier':
        recommandations.append("⚠️ Complètement de dossier")
        
        # Vérifier les pièces manquantes
        pieces_manquantes = candidat.pieces_manquantes.all()
        if pieces_manquantes:
            recommandations.append("📄 Pièces manquantes à fournir :")
            for piece in pieces_manquantes:
                recommandations.append(f"   • {piece.description}")
        
        # Recommandations selon le score
        if score_total < 60:
            recommandations.append("🎓 Stages recommandés :")
            recommandations.append("   • Stage en topographie : 2 semaines")
            recommandations.append("   • Stage en géodésie : 2 semaines")
        
        if score_total < 70:
            recommandations.append("📚 Cours complémentaires recommandés")
    
    elif decision == 'invitation_soutenance':
        recommandations.append("🎓 Invitation à la soutenance")
        recommandations.append("📚 Formation complémentaire requise")
        recommandations.append("🔄 Possibilité de nouvelle demande après formation")
    
    elif decision == 'invitation_concours':
        recommandations.append("🎓 Invitation au concours")
        recommandations.append("📚 Formation complémentaire requise")
        recommandations.append("🔄 Possibilité de nouvelle demande après formation")
    
    else:  # non_equivalent
        recommandations.append("❌ Équivalence refusée")
        recommandations.append("📚 Formation complémentaire requise")
        recommandations.append("🔄 Possibilité de nouvelle demande après formation")
    
    return "\n".join(recommandations)

def creer_notification(destinataire, type_notification, titre, message, dossier=None):
    """Fonction utilitaire pour créer des notifications"""
    notification = Notification.objects.create(
        destinataire=destinataire,
        type_notification=type_notification,
        titre=titre,
        message=message,
        dossier=dossier
    )
    return notification

@login_required
def recherche_avancee(request):
    """Recherche avancée dans les dossiers"""
    query = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    professeur = request.GET.get('professeur', '')
    
    dossiers = Dossier.objects.all()
    
    if query:
        dossiers = dossiers.filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query) |
            Q(candidat__nom__icontains=query) |
            Q(candidat__pays_origine__icontains=query)
        )
    
    if statut:
        dossiers = dossiers.filter(statut=statut)
    
    if date_debut:
        dossiers = dossiers.filter(date_reception__gte=date_debut)
    
    if date_fin:
        dossiers = dossiers.filter(date_reception__lte=date_fin)
    
    if professeur:
        dossiers = dossiers.filter(professeurs__username__icontains=professeur)
    
    # Statistiques de recherche
    total_trouve = dossiers.count()
    par_statut = {
        'non_traite': dossiers.filter(statut='non_traite').count(),
        'en_cours': dossiers.filter(statut='en_cours').count(),
        'traite': dossiers.filter(statut='traite').count(),
    }
    
    context = {
        'dossiers': dossiers,
        'query': query,
        'statut': statut,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'professeur': professeur,
        'total_trouve': total_trouve,
        'par_statut': par_statut,
    }
    
    return render(request, 'dossiers/recherche_avancee.html', context)

@login_required
def notifications(request):
    """Gestion des notifications"""
    notifications = request.user.notifications.all()
    
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            try:
                notification = Notification.objects.get(id=notification_id, destinataire=request.user)
                notification.lu = True
                notification.save()
                return JsonResponse({'success': True})
            except Notification.DoesNotExist:
                return JsonResponse({'success': False})
    
    context = {
        'notifications': notifications,
        'non_lues': notifications.filter(lu=False).count(),
    }
    
    return render(request, 'dossiers/notifications.html', context)

@login_required
def marquer_toutes_lues(request):
    """Marquer toutes les notifications comme lues"""
    request.user.notifications.filter(lu=False).update(lu=True)
    messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect('dossiers:notifications')

@login_required
def supprimer_notification(request, notification_id):
    """Supprimer une notification"""
    try:
        notification = Notification.objects.get(id=notification_id, destinataire=request.user)
        notification.delete()
        messages.success(request, "Notification supprimée avec succès.")
    except Notification.DoesNotExist:
        messages.error(request, "Notification non trouvée.")
    
    return redirect('dossiers:notifications')

@login_required
def import_csv_dossiers(request):
    """Importer des dossiers depuis un fichier CSV"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            try:
                # Vérifier l'extension du fichier
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, "Veuillez sélectionner un fichier CSV valide.")
                    return render(request, 'dossiers/import_csv.html')
                
                # Lire le fichier CSV
                import csv
                from io import StringIO
                
                # Décoder le contenu du fichier
                content = csv_file.read().decode('utf-8')
                csv_data = StringIO(content)
                
                # Parser le CSV
                reader = csv.DictReader(csv_data)
                
                                                 # Vérifier les colonnes requises
                required_columns = ['numero', 'demandeur_candidat', 'reference', 'date_envoi', 'date_reception', 'diplome', 'universite', 'pays', 'avis_commission']
                if not all(col in reader.fieldnames for col in required_columns):
                    messages.error(request, f"Le fichier CSV doit contenir les colonnes : {', '.join(required_columns)}")
                    return render(request, 'dossiers/import_csv.html')
                
                # Traiter chaque ligne
                dossiers_crees = 0
                dossiers_erreurs = 0
                
                for row_num, row in enumerate(reader, start=2):  # Commencer à 2 car la ligne 1 est l'en-tête
                    try:
                        # Créer le dossier traité directement
                        dossier_traite = DossierTraite.objects.create(
                            numero=row['numero'].strip(),
                            demandeur_candidat=row['demandeur_candidat'].strip(),
                            reference=row['reference'].strip(),
                            date_envoi=row.get('date_envoi', timezone.now().date()),
                            date_reception=row.get('date_reception', timezone.now().date()),
                            diplome=row['diplome'].strip(),
                            universite=row['universite'].strip(),
                            pays=row['pays'].strip(),
                            avis_commission=row['avis_commission'].strip(),
                            reference_reception=row.get('reference_reception', ''),
                            universite_autre=row.get('universite_autre', ''),
                            pays_autre=row.get('pays_autre', ''),
                            date_avis=row.get('date_avis', None),
                            date_decision=row.get('date_decision', None),
                            cree_par=request.user
                        )
                        
                        dossiers_crees += 1
                        
                    except Exception as e:
                        dossiers_erreurs += 1
                        messages.warning(request, f"Erreur ligne {row_num}: {str(e)}")
                
                if dossiers_crees > 0:
                    messages.success(request, f"{dossiers_crees} dossiers importés avec succès depuis le fichier CSV.")
                if dossiers_erreurs > 0:
                    messages.warning(request, f"{dossiers_erreurs} dossiers n'ont pas pu être importés.")
                
                return redirect('dossiers:dossiers_traites_admin')
                
            except Exception as e:
                messages.error(request, f"Erreur lors de l'import : {str(e)}")
        else:
            messages.error(request, "Veuillez sélectionner un fichier CSV.")
    
    return render(request, 'dossiers/import_csv.html')

@login_required
def import_csv_auto(request):
    """Import automatique de tous les dossiers depuis un fichier CSV"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    # Logique d'import automatique similaire mais sans interface utilisateur
    # Cette fonction peut être appelée par un script ou une tâche planifiée
    
    messages.success(request, "Import automatique CSV déclenché avec succès.")
    return redirect('dossiers:dossiers_traites_admin')

@login_required
def rapports_statistiques(request):
    """Génération de rapports et statistiques"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    # Statistiques générales
    total_dossiers = Dossier.objects.count()
    dossiers_non_traites = Dossier.objects.filter(statut='non_traite').count()
    dossiers_en_cours = Dossier.objects.filter(statut='en_cours').count()
    dossiers_traites = Dossier.objects.filter(statut='traite').count()
    
    # Statistiques par professeur
    professeurs_stats = []
    professeurs = CustomUser.objects.filter(role='professeur')
    for prof in professeurs:
        dossiers_assignes = prof.dossiers_attribues.count()
        dossiers_traites_prof = prof.dossiers_attribues.filter(statut='traite').count()
        taux_traitement = (dossiers_traites_prof / dossiers_assignes * 100) if dossiers_assignes > 0 else 0
        
        professeurs_stats.append({
            'professeur': prof,
            'dossiers_assignes': dossiers_assignes,
            'dossiers_traites': dossiers_traites_prof,
            'taux_traitement': round(taux_traitement, 1)
        })
    
    # Statistiques par mois
    from django.db.models import Count
    from django.db.models.functions import TruncMonth
    
    dossiers_par_mois = Dossier.objects.annotate(
        mois=TruncMonth('date_reception')
    ).values('mois').annotate(
        total=Count('id'),
        traites=Count('id', filter=Q(statut='traite')),
        en_cours=Count('id', filter=Q(statut='en_cours')),
        non_traites=Count('id', filter=Q(statut='non_traite'))
    ).order_by('mois')
    
    # Statistiques des évaluations (5 types de décisions)
    total_evaluations = DecisionCommission.objects.count()
    evaluations_completes = DecisionCommission.objects.filter(decision='equivalence_accorder').count()
    evaluations_conditionnelles = DecisionCommission.objects.filter(decision='completement_dossier').count()
    evaluations_invitation_soutenance = DecisionCommission.objects.filter(decision='invitation_soutenance').count()
    evaluations_invitation_concours = DecisionCommission.objects.filter(decision='invitation_concours').count()
    evaluations_refusees = DecisionCommission.objects.filter(decision='non_equivalent').count()
    
    # Moyenne des scores
    if total_evaluations > 0:
        moyenne_score = DecisionCommission.objects.aggregate(
            moyenne=models.Avg('score_total')
        )['moyenne']
    else:
        moyenne_score = 0
    
    context = {
        'total_dossiers': total_dossiers,
        'dossiers_non_traites': dossiers_non_traites,
        'dossiers_en_cours': dossiers_en_cours,
        'dossiers_traites': dossiers_traites,
        'professeurs_stats': professeurs_stats,
        'dossiers_par_mois': dossiers_par_mois,
        'total_evaluations': total_evaluations,
        'evaluations_completes': evaluations_completes,
        'evaluations_conditionnelles': evaluations_conditionnelles,
        'evaluations_invitation_soutenance': evaluations_invitation_soutenance,
        'evaluations_invitation_concours': evaluations_invitation_concours,
        'evaluations_refusees': evaluations_refusees,
        'moyenne_score': round(moyenne_score, 1) if moyenne_score else 0,
    }
    
    return render(request, 'dossiers/rapports_statistiques.html', context)

@login_required
def dashboard(request):
    """Tableau de bord principal - redirige selon le rôle"""
    if request.user.role == 'admin':
        return redirect('dossiers:admin_dossiers')
    else:
        return redirect('dossiers:professeur_dossiers')

@login_required
def admin_dossiers(request):
    """Tableau de bord administrateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossiers = Dossier.objects.all().order_by('-id')
    professeurs = CustomUser.objects.filter(role='professeur')
    
    # Filtrage par statut
    statut_filter = request.GET.get('statut')
    if statut_filter:
        dossiers = dossiers.filter(statut=statut_filter)
    
    # Calcul des statistiques
    total_dossiers = Dossier.objects.count()
    non_traites = Dossier.objects.filter(statut='non_traite').count()
    en_cours = Dossier.objects.filter(statut='en_cours').count()
    traites = Dossier.objects.filter(statut='traite').count()
    
    # Statistiques des dossiers traités (import Excel)
    total_dossiers_traites = DossierTraite.objects.count()
    
    context = {
        'dossiers': dossiers,
        'professeurs': professeurs,
        'statuts': Dossier.STATUT_CHOICES,
        'total_dossiers': total_dossiers,
        'non_traites': non_traites,
        'en_cours': en_cours,
        'traites': traites,
        'total_dossiers_traites': total_dossiers_traites,
    }
    return render(request, 'dossiers/admin_dashboard.html', context)

@login_required
def dossiers_traites(request):
    """Vue spéciale pour afficher les dossiers traités pour les administrateurs"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')

    # Récupérer uniquement les dossiers traités
    dossiers_traites = Dossier.objects.filter(statut='traite').order_by('-id')
    professeurs = CustomUser.objects.filter(role='professeur')

    # Filtres optionnels
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    professeur_filter = request.GET.get('professeur')

    if date_debut:
        dossiers_traites = dossiers_traites.filter(date_reception__gte=date_debut)
    if date_fin:
        dossiers_traites = dossiers_traites.filter(date_reception__lte=date_fin)
    if professeur_filter:
        dossiers_traites = dossiers_traites.filter(professeurs__id=professeur_filter)

    # Calcul des statistiques spécifiques aux dossiers traités
    total_traites = Dossier.objects.filter(statut='traite').count()
    traites_ce_mois = Dossier.objects.filter(statut='traite', date_reception__month=timezone.now().month).count()
    traites_ce_semaine = Dossier.objects.filter(statut='traite', date_reception__gte=timezone.now() - timezone.timedelta(days=7)).count()

    context = {
        'dossiers': dossiers_traites,
        'professeurs': professeurs,
        'total_traites': total_traites,
        'traites_ce_mois': traites_ce_mois,
        'traites_ce_semaine': traites_ce_semaine,
    }
    return render(request, 'dossiers/dossiers_traites.html', context)

@login_required
def gestion_dossiers(request):
    """Interface de gestion des dossiers"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossiers = Dossier.objects.all().order_by('-id')
    professeurs = CustomUser.objects.filter(role='professeur')
    
    # Filtrage par statut
    statut_filter = request.GET.get('statut')
    if statut_filter:
        dossiers = dossiers.filter(statut=statut_filter)
    
    # Filtrage par date
    date_filter = request.GET.get('date_reception')
    if date_filter:
        dossiers = dossiers.filter(date_reception=date_filter)
    
    # Calcul des statistiques
    total_dossiers = Dossier.objects.count()
    non_traites = Dossier.objects.filter(statut='non_traite').count()
    en_cours = Dossier.objects.filter(statut='en_cours').count()
    traites = Dossier.objects.filter(statut='traite').count()
    
    context = {
        'dossiers': dossiers,
        'professeurs': professeurs,
        'statuts': Dossier.STATUT_CHOICES,
        'total_dossiers': total_dossiers,
        'non_traites': non_traites,
        'en_cours': en_cours,
        'traites': traites,
    }
    return render(request, 'dossiers/gestion_dossiers.html', context)

@login_required
def ajouter_dossier(request):
    """Ajouter un nouveau dossier"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    if request.method == 'POST':
        reference = request.POST.get('reference')
        date_reference = request.POST.get('date_reception')
        description = request.POST.get('description')
        statut = request.POST.get('statut')
        
        try:
            dossier = Dossier.objects.create(
                titre=reference,  # Utiliser la référence comme titre
                description=description,
                statut=statut,
                date_reception=date_reference if date_reference else timezone.now().date()
            )
            
            # Gérer les pièces jointes séparées
            diplome = request.FILES.get('diplome')
            programme = request.FILES.get('programme')
            notes = request.FILES.get('notes')
            
            if diplome:
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=diplome,
                    description="Diplôme"
                )
            
            if programme:
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=programme,
                    description="Programme"
                )
            
            if notes:
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=notes,
                    description="Notes"
                )
            
            messages.success(request, f"Dossier '{reference}' créé avec succès")
        except Exception as e:
            messages.error(request, f"Erreur lors de la création : {str(e)}")
        
        return redirect('dossiers:gestion_dossiers')
    
    return redirect('dossiers:gestion_dossiers')

@login_required
def professeur_dossiers(request):
    """Tableau de bord professeur"""
    if request.user.role != 'professeur':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossiers_attribues = request.user.dossiers_attribues.all().order_by('-id')
    
    # Filtrage par statut
    statut_filter = request.GET.get('statut')
    if statut_filter:
        dossiers_attribues = dossiers_attribues.filter(statut=statut_filter)
    
    # Calcul des statistiques
    total_attribues = request.user.dossiers_attribues.count()
    a_traiter = request.user.dossiers_attribues.filter(statut='non_traite').count()
    en_cours = request.user.dossiers_attribues.filter(statut='en_cours').count()
    termines = request.user.dossiers_attribues.filter(statut='traite').count()
    
    context = {
        'dossiers': dossiers_attribues,
        'statuts': Dossier.STATUT_CHOICES,
        'total_attribues': total_attribues,
        'a_traiter': a_traiter,
        'en_cours': en_cours,
        'termines': termines,
        'notifications_recentes': request.user.notifications.filter(lu=False).order_by('-date_creation')[:3],
    }
    return render(request, 'dossiers/professeur_dashboard.html', context)

@login_required
def dossier_detail(request, dossier_id):
    """Détails d'un dossier"""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Vérifier les permissions
    if request.user.role == 'professeur' and dossier not in request.user.dossiers_attribues.all():
        messages.error(request, "Accès non autorisé à ce dossier")
        return redirect('dossiers:professeur_dossiers')
    
    # Vérifier si une évaluation complète existe déjà
    candidat = None
    consistance = None
    a_evaluation = False
    
    try:
        candidat_existant = Candidat.objects.get(dossier=dossier)
        candidat = candidat_existant
        # Vérifier si une consistance académique existe ET a des notes
        try:
            consistance = ConsistanceAcademique.objects.get(candidat=candidat_existant)
            # Vérifier si au moins une note a été saisie (tous les critères)
            notes_saisies = False
            
            # Vérifier les critères obligatoires et non-obligatoires
            if (consistance.sciences_geodesiques_note is not None or 
                consistance.topographie_note is not None or 
                consistance.photogrammetrie_note is not None or 
                consistance.cartographie_note is not None or
                consistance.droit_foncier_note is not None or
                consistance.sig_note is not None or
                consistance.teledetection_note is not None or
                consistance.stages_note is not None):
                notes_saisies = True
            
            # Vérifier les critères personnalisés
            if len(consistance.criteres_personnalises) > 0:
                for critere in consistance.criteres_personnalises:
                    if critere.get('note') is not None:
                        notes_saisies = True
                        break
            
            a_evaluation = notes_saisies
            
            # IMPORTANT: Si consistance existe, même sans notes, considérer qu'il y a une évaluation
            if consistance:
                a_evaluation = True
                
        except ConsistanceAcademique.DoesNotExist:
            a_evaluation = False
    except Candidat.DoesNotExist:
        a_evaluation = False
    
    # Détecter si on doit afficher la décision antérieure ou les nouvelles notes
    afficher_decision_anterieure = False
    if candidat and hasattr(candidat, 'etat_dossier') and candidat.etat_dossier:
        if candidat.etat_dossier.a_decision_anterieure:
            # Si il y a une décision antérieure ET une nouvelle évaluation, afficher les nouvelles notes
            if a_evaluation:
                afficher_decision_anterieure = False  # Afficher les nouvelles notes
            else:
                afficher_decision_anterieure = True   # Afficher l'ancienne décision
    
    # Récupérer les informations de décision antérieure
    decision_anterieure_info = None
    if candidat and hasattr(candidat, 'etat_dossier') and candidat.etat_dossier:
        if candidat.etat_dossier.a_decision_anterieure:
            decision_anterieure_info = {
                'a_decision_anterieure': True,
                'decision_anterieure': candidat.etat_dossier.decision_anterieure,
                'date_decision_anterieure': candidat.etat_dossier.date_decision_anterieure,
                'pieces_demandees': candidat.etat_dossier.pieces_demandees,
            }
    
    context = {
        'dossier': dossier,
        'candidat': candidat,
        'consistance': consistance,
        'pieces_jointes': dossier.pieces_jointes.all(),
        'historiques': dossier.historiques.all().order_by('-date_action'),
        'a_evaluation': a_evaluation,
        'afficher_decision_anterieure': afficher_decision_anterieure,
        'decision_anterieure_info': decision_anterieure_info,
    }
    return render(request, 'dossiers/dossier_detail.html', context)

@login_required
def affecter_dossier(request, dossier_id):
    """Affecter un dossier à des professeurs (admin seulement)"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    if request.method == 'POST':
        professeur_ids = request.POST.getlist('professeurs')
        professeurs = CustomUser.objects.filter(id__in=professeur_ids, role='professeur')
        
        dossier.professeurs.set(professeurs)
        dossier.statut = 'en_cours'
        dossier.save()
        
        # Créer un historique
        HistoriqueAction.objects.create(
            dossier=dossier,
            utilisateur=request.user,
            action=f"Dossier affecté à {', '.join([p.username for p in professeurs])}"
        )
        
        # Créer des notifications pour les professeurs
        notifications_creees = 0
        for professeur in professeurs:
            try:
                # Vérifier si une notification d'affectation existe déjà pour ce professeur et ce dossier
                notification_existante = Notification.objects.filter(
                    destinataire=professeur,
                    dossier=dossier,
                    type_notification='affectation'
                ).first()
                
                if not notification_existante:
                    creer_notification(
                        destinataire=professeur,
                        type_notification='affectation',
                        titre=f"Nouveau dossier assigné",
                        message=f"Le dossier '{dossier.titre}' vous a été assigné pour traitement.",
                        dossier=dossier
                    )
                    notifications_creees += 1
                else:
                    # Mettre à jour la notification existante si nécessaire
                    notification_existante.lu = False
                    notification_existante.save()
                    notifications_creees += 1
                    
            except Exception as e:
                print(f"Erreur lors de la création de notification pour {professeur.username}: {e}")
                # Continuer malgré l'erreur pour ne pas bloquer l'affectation
        
        messages.success(request, f"Dossier affecté avec succès à {len(professeurs)} professeur(s).")
        return redirect('dossiers:dossier_detail', dossier_id=dossier.id)
    
    # Calculer les statistiques des professeurs
    professeurs = CustomUser.objects.filter(role='professeur')
    professeurs_stats = []
    
    for professeur in professeurs:
        dossiers_en_cours = professeur.dossiers_attribues.filter(statut='en_cours').count()
        dossiers_traites = professeur.dossiers_attribues.filter(statut='traite').count()
        total_dossiers = professeur.dossiers_attribues.count()
        
        professeurs_stats.append({
            'professeur': professeur,
            'dossiers_en_cours': dossiers_en_cours,
            'dossiers_traites': dossiers_traites,
            'total_dossiers': total_dossiers,
        })
    
    context = {
        'dossier': dossier,
        'professeurs': professeurs,
        'professeurs_stats': professeurs_stats,
    }
    return render(request, 'dossiers/affecter_dossier.html', context)







@login_required
def etat_dossier(request, dossier_id):
    """Vue pour gérer la grille d'évaluation des dossiers (nouveau ou existant)"""
    if request.user.role != 'professeur':
        messages.error(request, "Seuls les professeurs peuvent gérer la grille d'évaluation des dossiers")
        return redirect('dossiers:dossier_detail', dossier_id=dossier_id)
    
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    try:
        candidat = Candidat.objects.get(dossier=dossier)
    except Candidat.DoesNotExist:
        # Créer un candidat par défaut si aucun n'existe
        candidat = Candidat.objects.create(
            dossier=dossier,
            nom=f"Candidat {dossier.titre}",
            date_arrivee=dossier.date_reception,
            pays_origine="Non spécifié"
        )
    
            # Récupérer ou créer la grille d'évaluation du dossier
    etat, created = EtatDossier.objects.get_or_create(
        candidat=candidat,
        defaults={
            'est_nouveau_dossier': True,
            'a_decision_anterieure': False,
        }
    )
    
    if request.method == 'POST':
        # Traiter les données du formulaire
        est_nouveau = request.POST.get('est_nouveau_dossier') == 'on'
        est_existant = request.POST.get('est_dossier_existant') == 'on'
        
        # Si l'un est coché, l'autre est forcément décoché
        if est_nouveau:
            etat.est_nouveau_dossier = True
        elif est_existant:
            etat.est_nouveau_dossier = False
        else:
            # Par défaut, nouveau dossier
            etat.est_nouveau_dossier = True
        
        if not etat.est_nouveau_dossier:
            # Si ce n'est pas un nouveau dossier, on demande les détails des décisions antérieures
            etat.a_decision_anterieure = request.POST.get('a_decision_anterieure') == 'on'
            
            if etat.a_decision_anterieure:
                date_decision = request.POST.get('date_decision_anterieure', '')
                if date_decision:
                    try:
                        etat.date_decision_anterieure = datetime.strptime(date_decision, '%Y-%m-%d').date()
                    except ValueError:
                        pass
                etat.decision_anterieure = request.POST.get('decision_anterieure', '')
            
            # Pièces demandées (liste prédéfinie)
            pieces_demandees = [
                "Les copies certifiées des deux diplômes obtenus",
                "Un justificatif des années d'études pour le Bachelor et le Master",
                "Le programme détaillé des cours du Bachelor et du Master (version originale + traduction en français)",
                "Les relevés de notes du Bachelor et du Master traduits en français",
                "Des attestations ou rapports de stage en topographie, géodésie, photogrammétrie, techniques cadastrales",
                "Un CV du candidat",
                "Une copie de la Carte d'Identité Nationale"
            ]
            etat.pieces_demandees = "\n".join([f"• {piece}" for piece in pieces_demandees])
        
        etat.save()
        
        messages.success(request, "Grille d'évaluation du dossier mise à jour avec succès")
        
        # Redirection selon la grille d'évaluation du dossier
        if etat.est_nouveau_dossier:
            # Si nouveau dossier (Oui), on passe à la consistance académique
            return redirect('dossiers:consistance_academique', dossier_id=dossier_id)
        else:
            # Si dossier existant (Non), on reste sur cette page pour voir les décisions antérieures
            return redirect('dossiers:etat_dossier', dossier_id=dossier_id)
    
    context = {
        'dossier': dossier,
        'candidat': candidat,
        'etat': etat,
    }
    return render(request, 'dossiers/etat_dossier.html', context)

@login_required
def consistance_academique(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Vérifier que l'utilisateur est un professeur uniquement
    if request.user.role != 'professeur':
        messages.error(request, "Accès non autorisé. Seuls les professeurs peuvent effectuer l'évaluation académique.")
        return redirect('dossiers:dossier_detail', dossier_id=dossier_id)
    
    # Vérifier si un candidat existe déjà pour ce dossier
    try:
        candidat = Candidat.objects.get(dossier=dossier)
    except Candidat.DoesNotExist:
        # Créer un candidat par défaut si aucun n'existe
        candidat = Candidat.objects.create(
            dossier=dossier,
            nom=f"Candidat {dossier.titre}",
            date_arrivee=dossier.date_reception,
            pays_origine="Non spécifié"
        )
    
    # Récupérer ou créer ConsistanceAcademique - SIMPLE ET DIRECT
    try:
        consistance = ConsistanceAcademique.objects.get(candidat=candidat)
    except ConsistanceAcademique.DoesNotExist:
        consistance = ConsistanceAcademique(candidat=candidat)
        consistance.save()  # Créer l'objet d'abord
    
    # Récupérer la structure globale mise à jour par l'admin
    try:
        structure_globale = StructureEvaluationGlobale.objects.first()
        if not structure_globale:
            # Créer une structure par défaut si elle n'existe pas
            structure_globale = StructureEvaluationGlobale.objects.create()
        
        # S'assurer que les champs JSON ne sont pas None
        if structure_globale.competences_criteres_fixes is None:
            structure_globale.competences_criteres_fixes = {}
        if structure_globale.criteres_fixes_supprimes is None:
            structure_globale.criteres_fixes_supprimes = []
        if structure_globale.criteres_personnalises_globaux is None:
            structure_globale.criteres_personnalises_globaux = []
        
        # Trier les critères personnalisés par ordre d'ajout (par ID) pour garantir l'ordre d'affichage
        if structure_globale.criteres_personnalises_globaux:
            structure_globale.criteres_personnalises_globaux.sort(key=lambda x: x.get('id', 0))
        
        # Initialiser les compétences par défaut si elles n'existent pas
        if 'sciences_geodesiques' not in structure_globale.competences_criteres_fixes or not structure_globale.competences_criteres_fixes['sciences_geodesiques']:
            structure_globale.competences_criteres_fixes['sciences_geodesiques'] = [
                "Théorique et pratique de la géodésie",
                "Mesures géodésiques", 
                "Calculs géodésiques"
            ]
        if 'topographie' not in structure_globale.competences_criteres_fixes or not structure_globale.competences_criteres_fixes['topographie']:
            structure_globale.competences_criteres_fixes['topographie'] = [
                "Théorique et pratique de la topographie",
                "Topométrique et instrumentation",
                "Techniques de mensuration"
            ]
        if 'photogrammetrie' not in structure_globale.competences_criteres_fixes or not structure_globale.competences_criteres_fixes['photogrammetrie']:
            structure_globale.competences_criteres_fixes['photogrammetrie'] = [
                "Base et approfondie de la photogrammétrie",
                "Mise en place des photographies aériennes",
                "Aérotriangulation",
                "Restitution photogrammétrique",
                "Génération de produits dérivés (MNT/Ortho)",
                "Drone"
            ]
        if 'cartographie' not in structure_globale.competences_criteres_fixes or not structure_globale.competences_criteres_fixes['cartographie']:
            structure_globale.competences_criteres_fixes['cartographie'] = [
                "Théorique et pratique de la cartographie",
                "Techniques de cartographie",
                "Produits cartographiques"
            ]
        if 'droit_foncier' not in structure_globale.competences_criteres_fixes or not structure_globale.competences_criteres_fixes['droit_foncier']:
            structure_globale.competences_criteres_fixes['droit_foncier'] = [
                "Droit foncier",
                "Cadastre",
                "Aménagements fonciers"
            ]
        if 'sig' not in structure_globale.competences_criteres_fixes or not structure_globale.competences_criteres_fixes['sig']:
            structure_globale.competences_criteres_fixes['sig'] = [
                "Systèmes d'Information Géographique",
                "Applications SIG",
                "Analyse spatiale"
            ]
        if 'teledetection' not in structure_globale.competences_criteres_fixes or not structure_globale.competences_criteres_fixes['teledetection']:
            structure_globale.competences_criteres_fixes['teledetection'] = [
                "Télédétection",
                "Traitement d'images",
                "Applications de télédétection"
            ]
            
    except Exception as e:
        print(f"Erreur lors de la récupération de la structure globale: {e}")
        # Créer une structure temporaire par défaut
        class StructureTemporaire:
            def __init__(self):
                self.sciences_geodesiques_note_max = 15
                self.topographie_note_max = 16
                self.photogrammetrie_note_max = 15
                self.cartographie_note_max = 12
                self.droit_foncier_note_max = 10
                self.sig_note_max = 12
                self.teledetection_note_max = 10
                self.stages_note_max = 10
                self.criteres_personnalises_globaux = []
                self.competences_criteres_fixes = {}
                self.criteres_fixes_supprimes = []
                self.date_modification = timezone.now()
        structure_globale = StructureTemporaire()
        
        # Trier les critères personnalisés par ordre d'ajout (par ID) pour garantir l'ordre d'affichage
        if structure_globale.criteres_personnalises_globaux:
            structure_globale.criteres_personnalises_globaux.sort(key=lambda x: x.get('id', 0))
    
    if request.method == 'POST':
        # VÉRIFIER si c'est un retour à l'admin
        if request.POST.get('retour_admin'):
            # RETOUR À L'ADMIN : Traitement spécial sans toucher aux notes
            message_professeur = request.POST.get('message_professeur', '').strip()
            
            # Créer notification directement et rediriger
            historique_affectation = HistoriqueAction.objects.filter(
                dossier=dossier,
                action__icontains='affecté'
            ).order_by('-date_action').first()
            
            if historique_affectation:
                admin_affecteur = historique_affectation.utilisateur
            else:
                admins = CustomUser.objects.filter(role='admin')
                admin_affecteur = admins.first() if admins.exists() else None
            
            if admin_affecteur:
                # Récupérer la note actuelle SANS la modifier
                consistance_actuelle = ConsistanceAcademique.objects.get(candidat=candidat)
                note_totale_actuelle = consistance_actuelle.note_totale
                
                message_base = f"Le professeur {request.user.get_full_name() or request.user.username} a terminé l'évaluation du dossier '{dossier.titre}' et demande la validation. Score total : {note_totale_actuelle}/100 points."
                
                if message_professeur:
                    message_base += f"\n\nMessage du professeur : {message_professeur}"
                
                creer_notification(
                    destinataire=admin_affecteur,
                    type_notification='traitement',
                    titre=f"Retour du dossier traité : {dossier.titre}",
                    message=message_base,
                    dossier=dossier
                )
                messages.success(request, "Retour à l'administrateur effectué avec succès. Notification envoyée.")
            
            return redirect('dossiers:dossier_detail', dossier_id=dossier_id)
        
        # VALIDATION DES NOTES OBLIGATOIRES
        notes_manquantes = []
        
        # Vérifier les critères fixes obligatoires
        if 'sciences_geodesiques' not in structure_globale.criteres_fixes_supprimes:
            if not request.POST.get('sciences_geodesiques_note') or not request.POST.get('sciences_geodesiques_note').strip():
                notes_manquantes.append("Sciences géodésiques")
        
        if 'topographie' not in structure_globale.criteres_fixes_supprimes:
            if not request.POST.get('topographie_note') or not request.POST.get('topographie_note').strip():
                notes_manquantes.append("Topographie")
        
        if 'photogrammetrie' not in structure_globale.criteres_fixes_supprimes:
            if not request.POST.get('photogrammetrie_note') or not request.POST.get('photogrammetrie_note').strip():
                notes_manquantes.append("Photogrammétrie")
        
        if 'cartographie' not in structure_globale.criteres_fixes_supprimes:
            if not request.POST.get('cartographie_note') or not request.POST.get('cartographie_note').strip():
                notes_manquantes.append("Cartographie")
        
        if 'droit_foncier' not in structure_globale.criteres_fixes_supprimes:
            if not request.POST.get('droit_foncier_note') or not request.POST.get('droit_foncier_note').strip():
                notes_manquantes.append("Droit foncier")
        
        if 'sig' not in structure_globale.criteres_fixes_supprimes:
            if not request.POST.get('sig_note') or not request.POST.get('sig_note').strip():
                notes_manquantes.append("SIG")
        
        if 'teledetection' not in structure_globale.criteres_fixes_supprimes:
            if not request.POST.get('teledetection_note') or not request.POST.get('teledetection_note').strip():
                notes_manquantes.append("Télédétection")
        
        # Vérifier la note des stages
        if not request.POST.get('stages_note') or not request.POST.get('stages_note').strip():
            notes_manquantes.append("Stages")
        
        # Vérifier les notes des critères personnalisés
        if structure_globale.criteres_personnalises_globaux:
            for critere in structure_globale.criteres_personnalises_globaux:
                critere_id = critere.get('id')
                note_critere = request.POST.get(f'note_critere_personnalise_{critere_id}')
                if not note_critere or not note_critere.strip():
                    notes_manquantes.append(f"Critère personnalisé : {critere.get('nom')}")
        
        # Si des notes sont manquantes, afficher l'erreur et ne pas sauvegarder
        if notes_manquantes:
            messages.error(request, f"❌ ERREUR : Vous devez remplir TOUTES les notes obligatoires !\n\nNotes manquantes : {', '.join(notes_manquantes)}")
            return render(request, 'dossiers/consistance_academique.html', context)
        
        # SAUVEGARDE NORMALE DES NOTES (seulement si pas de retour admin)
        # Sciences géodésiques
        sciences_geodesiques_note = request.POST.get('sciences_geodesiques_note')
        consistance.sciences_geodesiques_contenus = request.POST.get('sciences_geodesiques_contenus', '')
        consistance.sciences_geodesiques_commentaires = request.POST.get('sciences_geodesiques_commentaires', '')
        
        if sciences_geodesiques_note and sciences_geodesiques_note.strip():
            try:
                note_saisie = int(sciences_geodesiques_note)
                note_max = structure_globale.sciences_geodesiques_note_max
                if note_saisie < 0 or note_saisie > note_max:
                    messages.error(request, f"❌ ERREUR : La note pour Sciences géodésiques doit être entre 0 et {note_max} (saisie: {note_saisie})")
                    return render(request, 'dossiers/consistance_academique.html', context)
                consistance.sciences_geodesiques_note = note_saisie
            except ValueError:
                messages.error(request, "❌ ERREUR : La note pour Sciences géodésiques doit être un nombre entier valide")
                return render(request, 'dossiers/consistance_academique.html', context)
        else:
            consistance.sciences_geodesiques_note = None
        
        # Topographie
        topographie_note = request.POST.get('topographie_note')
        consistance.topographie_contenus = request.POST.get('topographie_contenus', '')
        consistance.topographie_commentaires = request.POST.get('topographie_commentaires', '')
        
        if topographie_note and topographie_note.strip():
            try:
                note_saisie = int(topographie_note)
                note_max = structure_globale.topographie_note_max
                if note_saisie < 0 or note_saisie > note_max:
                    messages.error(request, f"❌ ERREUR : La note pour Topographie doit être entre 0 et {note_max} (saisie: {note_saisie})")
                    return render(request, 'dossiers/consistance_academique.html', context)
                consistance.topographie_note = note_saisie
            except ValueError:
                messages.error(request, "❌ ERREUR : La note pour Topographie doit être un nombre entier valide")
                return render(request, 'dossiers/consistance_academique.html', context)
        else:
            consistance.topographie_note = None

        
        # Photogrammétrie
        consistance.photogrammetrie_contenus = request.POST.get('photogrammetrie_contenus', '')
        consistance.photogrammetrie_commentaires = request.POST.get('photogrammetrie_commentaires', '')
        photogrammetrie_note = request.POST.get('photogrammetrie_note')
        
        if photogrammetrie_note and photogrammetrie_note.strip():
            try:
                note_saisie = int(photogrammetrie_note)
                note_max = structure_globale.photogrammetrie_note_max
                if note_saisie < 0 or note_saisie > note_max:
                    messages.error(request, f"❌ ERREUR : La note pour Photogrammétrie doit être entre 0 et {note_max} (saisie: {note_saisie})")
                    return render(request, 'dossiers/consistance_academique.html', context)
                consistance.photogrammetrie_note = note_saisie
            except ValueError:
                messages.error(request, "❌ ERREUR : La note pour Photogrammétrie doit être un nombre entier valide")
                return render(request, 'dossiers/consistance_academique.html', context)
        else:
            consistance.photogrammetrie_note = None
        
        # Checkboxes Photogrammétrie
        consistance.photogrammetrie_base_approfondie = 'photogrammetrie_base_approfondie' in request.POST
        consistance.photogrammetrie_photographies_aeriennes = 'photogrammetrie_photographies_aeriennes' in request.POST
        consistance.photogrammetrie_aerotriangulation = 'photogrammetrie_aerotriangulation' in request.POST
        consistance.photogrammetrie_restitution = 'photogrammetrie_restitution' in request.POST
        consistance.photogrammetrie_produits_derives = 'photogrammetrie_produits_derives' in request.POST
        consistance.photogrammetrie_drone = 'photogrammetrie_drone' in request.POST
        
        # Cartographie
        consistance.cartographie_contenus = request.POST.get('cartographie_contenus', '')
        consistance.cartographie_commentaires = request.POST.get('cartographie_commentaires', '')
        cartographie_note = request.POST.get('cartographie_note')
        
        if cartographie_note and cartographie_note.strip():
            try:
                note_saisie = int(cartographie_note)
                note_max = structure_globale.cartographie_note_max
                if note_saisie < 0 or note_saisie > note_max:
                    messages.error(request, f"❌ ERREUR : La note pour Cartographie doit être entre 0 et {note_max} (saisie: {note_saisie})")
                    return render(request, 'dossiers/consistance_academique.html', context)
                consistance.cartographie_note = note_saisie
            except ValueError:
                messages.error(request, "❌ ERREUR : La note pour Cartographie doit être un nombre entier valide")
                return render(request, 'dossiers/consistance_academique.html', context)
        else:
            consistance.cartographie_note = None
        consistance.cartographie_drone = 'cartographie_drone' in request.POST
        
        # Droit foncier
        consistance.droit_foncier_contenus = request.POST.get('droit_foncier_contenus', '')
        consistance.droit_foncier_commentaires = request.POST.get('droit_foncier_commentaires', '')
        droit_foncier_note = request.POST.get('droit_foncier_note')
        
        if droit_foncier_note and droit_foncier_note.strip():
            try:
                note_saisie = int(droit_foncier_note)
                note_max = structure_globale.droit_foncier_note_max
                if note_saisie < 0 or note_saisie > note_max:
                    messages.error(request, f"❌ ERREUR : La note pour Droit foncier doit être entre 0 et {note_max} (saisie: {note_saisie})")
                    return render(request, 'dossiers/consistance_academique.html', context)
                consistance.droit_foncier_note = note_saisie
            except ValueError:
                messages.error(request, "❌ ERREUR : La note pour Droit foncier doit être un nombre entier valide")
                return render(request, 'dossiers/consistance_academique.html', context)
        else:
            consistance.droit_foncier_note = None
        
        # SIG
        consistance.sig_contenus = request.POST.get('sig_contenus', '')
        consistance.sig_commentaires = request.POST.get('sig_commentaires', '')
        sig_note = request.POST.get('sig_note')
        
        if sig_note and sig_note.strip():
            try:
                note_saisie = int(sig_note)
                note_max = structure_globale.sig_note_max
                if note_saisie < 0 or note_saisie > note_max:
                    messages.error(request, f"❌ ERREUR : La note pour SIG doit être entre 0 et {note_max} (saisie: {note_saisie})")
                    return render(request, 'dossiers/consistance_academique.html', context)
                consistance.sig_note = note_saisie
            except ValueError:
                messages.error(request, "❌ ERREUR : La note pour SIG doit être un nombre entier valide")
                return render(request, 'dossiers/consistance_academique.html', context)
        else:
            consistance.sig_note = None
        
        # Télédétection
        consistance.teledetection_contenus = request.POST.get('teledetection_contenus', '')
        consistance.teledetection_commentaires = request.POST.get('teledetection_commentaires', '')
        teledetection_note = request.POST.get('teledetection_note')
        
        if teledetection_note and teledetection_note.strip():
            try:
                note_saisie = int(teledetection_note)
                note_max = structure_globale.teledetection_note_max
                if note_saisie < 0 or note_saisie > note_max:
                    messages.error(request, f"❌ ERREUR : La note pour Télédétection doit être entre 0 et {note_max} (saisie: {note_saisie})")
                    return render(request, 'dossiers/consistance_academique.html', context)
                consistance.teledetection_note = note_saisie
            except ValueError:
                messages.error(request, "❌ ERREUR : La note pour Télédétection doit être un nombre entier valide")
                return render(request, 'dossiers/consistance_academique.html', context)
        else:
            consistance.teledetection_note = None
        
        # Stages et professionnalisation
        consistance.stages_contenus = request.POST.get('stages_contenus', '')
        consistance.stages_commentaires = request.POST.get('stages_commentaires', '')
        stages_note = request.POST.get('stages_note')
        
        if stages_note and stages_note.strip():
            try:
                note_saisie = int(stages_note)
                note_max = structure_globale.stages_note_max
                if note_saisie < 0 or note_saisie > note_max:
                    messages.error(request, f"❌ ERREUR : La note pour Stages doit être entre 0 et {note_max} (saisie: {note_saisie})")
                    return render(request, 'dossiers/consistance_academique.html', context)
                consistance.stages_note = note_saisie
            except ValueError:
                messages.error(request, "❌ ERREUR : La note pour Stages doit être un nombre entier valide")
                return render(request, 'dossiers/consistance_academique.html', context)
        else:
            consistance.stages_note = None
        
        # Stages par défaut (seulement s'ils ne sont pas supprimés par l'admin)
        if not hasattr(structure_globale, 'stages_defaut_supprimes') or structure_globale.stages_defaut_supprimes is None:
            structure_globale.stages_defaut_supprimes = []
            
        if 'stage_conservation_fonciere' not in structure_globale.stages_defaut_supprimes:
            consistance.stage_conservation_fonciere = 'stage_conservation_fonciere' in request.POST
        if 'stage_cadastre' not in structure_globale.stages_defaut_supprimes:
            consistance.stage_cadastre = 'stage_cadastre' in request.POST
        if 'stage_topographie' not in structure_globale.stages_defaut_supprimes:
            consistance.stage_topographie = 'stage_topographie' in request.POST
        if 'stage_geodesie' not in structure_globale.stages_defaut_supprimes:
            consistance.stage_geodesie = 'stage_geodesie' in request.POST
        if 'stage_photogrammetrie' not in structure_globale.stages_defaut_supprimes:
            consistance.stage_photogrammetrie = 'stage_photogrammetrie' in request.POST
        consistance.stage_techniques_cadastrales = 'stage_techniques_cadastrales' in request.POST
        
        # Stages configurables
        stages_configurables_cochees = []
        if hasattr(structure_globale, 'stages_configurables') and structure_globale.stages_configurables:
            for stage in structure_globale.stages_configurables:
                if request.POST.get(f'stage_configurable_{stage["id"]}'):
                    stages_configurables_cochees.append(stage["id"])
        consistance.stages_configurables_cochees = stages_configurables_cochees
        
        # Gestion des boutons stages (nouveaux champs) - mutuellement exclusifs
        stages_status = request.POST.get('stages_status')
        consistance.stages_acheves = stages_status == 'acheves'
        consistance.stages_non_acheves = stages_status == 'non_acheves'
        consistance.message_stages_non_acheves = request.POST.get('message_stages_non_acheves', '')
        
        # Gestion des critères personnalisés (seuls les administrateurs peuvent ajouter/supprimer)
        action_critere = request.POST.get('action_critere')
        if action_critere == 'ajouter' and request.user.role == 'admin':
            nom_critere = request.POST.get('nom_critere_personnalise', '').strip()
            note_max_critere = request.POST.get('note_max_critere_personnalise', 0)
            if nom_critere and note_max_critere:
                try:
                    note_max = int(note_max_critere)
                    nouveau_critere = {
                        'id': len(consistance.criteres_personnalises) + 1,
                        'nom': nom_critere,
                        'note_max': note_max,
                        'note': None,
                        'contenus': '',
                        'commentaires': ''
                    }
                    consistance.criteres_personnalises.append(nouveau_critere)
                    messages.success(request, f"Critère '{nom_critere}' ajouté avec succès.")
                except ValueError:
                    pass
        elif action_critere == 'supprimer' and request.user.role == 'admin':
            critere_id = request.POST.get('critere_id')
            if critere_id:
                try:
                    critere_id = int(critere_id)
                    critere_a_supprimer = None
                    for critere in consistance.criteres_personnalises:
                        if critere.get('id') == critere_id:
                            critere_a_supprimer = critere
                            break
                    
                    if critere_a_supprimer:
                        consistance.criteres_personnalises = [
                            c for c in consistance.criteres_personnalises 
                            if c.get('id') != critere_id
                        ]
                        messages.success(request, f"Critère '{critere_a_supprimer.get('nom')}' supprimé avec succès.")
                except ValueError:
                    pass
        
        # Gestion des compétences pour chaque critère personnalisé (seuls les administrateurs peuvent ajouter/supprimer)
        for critere in consistance.criteres_personnalises:
            critere_id = critere.get('id')
            # Initialisation des listes si absentes
            if 'competences' not in critere:
                critere['competences'] = []
            if 'competences_cochees' not in critere:
                critere['competences_cochees'] = []
            
            # Ajout d'une compétence (seuls les administrateurs)
            if request.POST.get(f'ajouter_competence_{critere_id}') and request.user.role == 'admin':
                nouvelle_comp = request.POST.get(f'nouvelle_competence_{critere_id}', '').strip()
                if nouvelle_comp:
                    critere['competences'].append(nouvelle_comp)
                    messages.success(request, f"Compétence '{nouvelle_comp}' ajoutée au critère '{critere.get('nom')}'.")
            
            # Suppression d'une compétence (seuls les administrateurs)
            for idx, comp in enumerate(critere['competences']):
                if request.POST.get(f'supprimer_competence_{critere_id}_{idx}') and request.user.role == 'admin':
                    critere['competences'].pop(idx)
                    # On retire aussi l'index des cochées si besoin
                    if idx in critere['competences_cochees']:
                        critere['competences_cochees'].remove(idx)
                    messages.success(request, f"Compétence '{comp}' supprimée du critère '{critere.get('nom')}'.")
                    break
            # Gestion des cases cochées
            competences_cochees = []
            for idx in range(len(critere['competences'])):
                if request.POST.get(f'competence_{critere_id}_{idx}'):
                    competences_cochees.append(idx)
            critere['competences_cochees'] = competences_cochees
            
            # Récupération de la note saisie manuellement par le professeur
            note_critere = request.POST.get(f'note_critere_personnalise_{critere_id}')
            if note_critere and note_critere.strip():
                try:
                    note_saisie = int(note_critere)
                    note_max = critere.get('note_max', 10)
                    
                    # Vérifier que la note ne dépasse pas la note maximale définie par l'admin
                    if note_saisie < 0:
                        messages.error(request, f"❌ ERREUR : La note pour '{critere.get('nom')}' ne peut pas être négative (saisie: {note_saisie})")
                        return render(request, 'dossiers/consistance_academique.html', context)
                    elif note_saisie > note_max:
                        messages.error(request, f"❌ ERREUR : La note pour '{critere.get('nom')}' ne peut pas dépasser {note_max} (saisie: {note_saisie})")
                        return render(request, 'dossiers/consistance_academique.html', context)
                    else:
                        critere['note'] = note_saisie
                except ValueError:
                    messages.error(request, f"❌ ERREUR : La note pour '{critere.get('nom')}' doit être un nombre entier valide")
                    return render(request, 'dossiers/consistance_academique.html', context)
            else:
                critere['note'] = None
        
        # SAUVEGARDE DIRECTE ET SIMPLE
        consistance.save()
        
        # Forcer une transaction commit
        from django.db import transaction
        transaction.commit()
        
        # Évaluer les critères obligatoires
        evaluation_resultats = consistance.evaluer_criteres_obligatoires()
        
        # Vérifier si le dossier est complètement traité (au moins une note saisie)
        notes_saisies = any([
            consistance.sciences_geodesiques_note is not None,
            consistance.topographie_note is not None,
            consistance.photogrammetrie_note is not None,
            consistance.cartographie_note is not None,
            consistance.droit_foncier_note is not None,
            consistance.sig_note is not None,
            consistance.teledetection_note is not None,
            consistance.stages_note is not None
        ])
        

        
        # Traitement normal des notifications après sauvegarde
        if notes_saisies:
            # Créer une notification pour l'admin qui a affecté le dossier
            # Chercher l'admin qui a affecté le dossier via l'historique
            historique_affectation = HistoriqueAction.objects.filter(
                dossier=dossier,
                action__icontains='affecté'
            ).order_by('-date_action').first()
            
            # Si pas d'historique, chercher tous les admins
            if historique_affectation:
                admin_affecteur = historique_affectation.utilisateur
            else:
                # Fallback : chercher tous les admins
                admins = CustomUser.objects.filter(role='admin')
                admin_affecteur = admins.first() if admins.exists() else None
            
            if admin_affecteur:
                creer_notification(
                    destinataire=admin_affecteur,
                    type_notification='traitement',
                    titre=f"Dossier prêt pour validation : {dossier.titre}",
                    message=f"Le professeur {request.user.get_full_name() or request.user.username} a terminé l'évaluation du dossier '{dossier.titre}'. Score total : {consistance.note_totale}/100 points. Le dossier est prêt pour validation et transfert vers les dossiers traités.",
                    dossier=dossier
                )
                
                messages.success(request, f"Consistance académique mise à jour avec succès. Notification envoyée à l'administrateur pour validation.")
            else:
                messages.error(request, "Aucun administrateur trouvé pour recevoir la notification.")
        else:
            messages.success(request, "Consistance académique mise à jour avec succès.")
            

        
        if evaluation_resultats['dossier_suffisant']:
            messages.success(request, "Tous les critères obligatoires sont acquis.")
        else:
            criteres_non_acquis = ", ".join(evaluation_resultats['criteres_non_acquis'])
            messages.error(request, f"⚠️ CRITÈRES OBLIGATOIRES NON ACQUIS : {criteres_non_acquis}. Le dossier sera automatiquement jugé insuffisant même avec un score total élevé (76-100 points).")
        
        # Plus de traitement de retour admin ici - déjà fait au début
        
        return redirect('dossiers:dossier_detail', dossier_id=dossier_id)
    
    # Évaluer les critères obligatoires pour l'affichage
    evaluation_resultats = consistance.evaluer_criteres_obligatoires()
    
    # Interpréter les résultats globaux
    interpretation_globale = consistance.interpreter_resultats_globaux()
    
    # Compétences par défaut pour les critères fixes
    compétences_sciences_geodesiques = [
        "Théorique et pratique de la géodésie",
        "Mesures géodésiques",
        "Calculs géodésiques"
    ]
    compétences_topographie = [
        "Théorique et pratique de la topographie",
        "Topométrique et instrumentation",
        "Techniques de mensuration"
    ]
    compétences_photogrammetrie = [
        "Base et approfondie de la photogrammétrie",
        "Mise en place des photographies aériennes",
        "Aérotriangulation",
        "Restitution photogrammétrique",
        "Génération de produits dérivés (MNT/Ortho)",
        "Drone"
    ]
    compétences_cartographie = [
        "Théorique et pratique de la cartographie",
        "Techniques de cartographie",
        "Produits cartographiques"
    ]
    compétences_droit_foncier = [
        "Droit foncier",
        "Cadastre",
        "Aménagements fonciers"
    ]
    compétences_sig = [
        "Systèmes d'Information Géographique",
        "Applications SIG",
        "Analyse spatiale"
    ]
    compétences_teledetection = [
        "Télédétection",
        "Traitement d'images",
        "Applications de télédétection"
    ]
    
    # Créer les listes de compétences cochées basées sur les champs booléens du modèle
    sciences_geodesiques_competences_cochees = []
    if consistance.sciences_geodesie_geometrique:
        sciences_geodesiques_competences_cochees.append(0)
    if consistance.sciences_astronomie_geodesie_spatiale:
        sciences_geodesiques_competences_cochees.append(1)
    if consistance.sciences_geodesie_physique:
        sciences_geodesiques_competences_cochees.append(2)
    if consistance.sciences_ajustements_compensations:
        sciences_geodesiques_competences_cochees.append(3)
    if consistance.sciences_systemes_referentiels:
        sciences_geodesiques_competences_cochees.append(4)
    if consistance.sciences_projections_cartographiques:
        sciences_geodesiques_competences_cochees.append(5)
    if consistance.sciences_geodesie_appliquee:
        sciences_geodesiques_competences_cochees.append(6)
    if consistance.sciences_gnss:
        sciences_geodesiques_competences_cochees.append(7)
    if consistance.sciences_micro_geodesie:
        sciences_geodesiques_competences_cochees.append(8)

    topographie_competences_cochees = []
    if consistance.topographie_theorique_pratique:
        topographie_competences_cochees.append(0)
    if consistance.topographie_topometrique_instrumentation:
        topographie_competences_cochees.append(1)
    if consistance.topographie_techniques_mensuration:
        topographie_competences_cochees.append(2)

    photogrammetrie_competences_cochees = []
    if consistance.photogrammetrie_base_approfondie:
        photogrammetrie_competences_cochees.append(0)
    if consistance.photogrammetrie_photographies_aeriennes:
        photogrammetrie_competences_cochees.append(1)
    if consistance.photogrammetrie_aerotriangulation:
        photogrammetrie_competences_cochees.append(2)
    if consistance.photogrammetrie_restitution:
        photogrammetrie_competences_cochees.append(3)
    if consistance.photogrammetrie_produits_derives:
        photogrammetrie_competences_cochees.append(4)
    if consistance.photogrammetrie_drone:
        photogrammetrie_competences_cochees.append(5)

    cartographie_competences_cochees = []
    if consistance.cartographie_topographique:
        cartographie_competences_cochees.append(0)
    if consistance.cartographie_representation_cartographique:
        cartographie_competences_cochees.append(1)
    if consistance.cartographie_thematique:
        cartographie_competences_cochees.append(2)
    if consistance.cartographie_semiologie_langage:
        cartographie_competences_cochees.append(3)
    if consistance.cartographie_dao_cao:
        cartographie_competences_cochees.append(4)
    if consistance.cartographie_drone:
        cartographie_competences_cochees.append(5)

    droit_foncier_competences_cochees = []
    if consistance.droit_foncier_droit:
        droit_foncier_competences_cochees.append(0)
    if consistance.droit_foncier_techniques_cadastrales:
        droit_foncier_competences_cochees.append(1)
    if consistance.droit_foncier_gestion_amenagement:
        droit_foncier_competences_cochees.append(2)
    if consistance.droit_foncier_reglementations:
        droit_foncier_competences_cochees.append(3)

    sig_competences_cochees = []
    if consistance.sig_bases:
        sig_competences_cochees.append(0)
    if consistance.sig_gestion_analyse_donnees:
        sig_competences_cochees.append(1)
    if consistance.sig_bases_donnees_geographiques:
        sig_competences_cochees.append(2)
    if consistance.sig_web_mapping:
        sig_competences_cochees.append(3)

    teledetection_competences_cochees = []
    if consistance.teledetection_bases_physiques:
        teledetection_competences_cochees.append(0)
    if consistance.teledetection_traitement_images:
        teledetection_competences_cochees.append(1)
    if consistance.teledetection_applications:
        teledetection_competences_cochees.append(2)

    context = {
        'dossier': dossier,
        'consistance': consistance,
        'evaluation_resultats': evaluation_resultats,
        'user': request.user,
        'interpretation_globale': interpretation_globale,
        'structure': structure_globale,  # Ajouter la structure globale
        'compétences_sciences_geodesiques': compétences_sciences_geodesiques,
        'compétences_topographie': compétences_topographie,
        'compétences_photogrammetrie': compétences_photogrammetrie,
        'compétences_cartographie': compétences_cartographie,
        'compétences_droit_foncier': compétences_droit_foncier,
        'compétences_sig': compétences_sig,
        'compétences_teledetection': compétences_teledetection,
        'sciences_geodesiques_competences_cochees': sciences_geodesiques_competences_cochees,
        'topographie_competences_cochees': topographie_competences_cochees,
        'photogrammetrie_competences_cochees': photogrammetrie_competences_cochees,
        'cartographie_competences_cochees': cartographie_competences_cochees,
        'droit_foncier_competences_cochees': droit_foncier_competences_cochees,
        'sig_competences_cochees': sig_competences_cochees,
        'teledetection_competences_cochees': teledetection_competences_cochees,
    }
    
    return render(request, 'dossiers/consistance_academique.html', context)

@login_required
def traiter_dossier(request, dossier_id):
    """Traiter un dossier (changer le statut)"""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Vérifier les permissions
    if request.user.role == 'professeur' and dossier not in request.user.dossiers_attribues.all():
        messages.error(request, "Accès non autorisé à ce dossier")
        return redirect('dossiers:professeur_dossiers')
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut in dict(Dossier.STATUT_CHOICES):
            ancien_statut = dossier.statut
            dossier.statut = nouveau_statut
            dossier.save()
            
            # Créer un historique
            HistoriqueAction.objects.create(
                dossier=dossier,
                utilisateur=request.user,
                action=f"Statut changé de {dict(Dossier.STATUT_CHOICES)[ancien_statut]} à {dict(Dossier.STATUT_CHOICES)[nouveau_statut]}"
            )
            
            # Si le dossier passe en traitement et qu'il n'y a pas encore d'évaluation
            try:
                candidat_existant = Candidat.objects.get(dossier=dossier)
                a_evaluation = True
            except Candidat.DoesNotExist:
                a_evaluation = False
            

            
            # Notifier l'administrateur si le dossier est traité
            if nouveau_statut == 'traite':
                # Vérifier s'il y a une décision antérieure
                try:
                    candidat = dossier.candidat
                    etat_dossier = candidat.etat_dossier
                    a_decision_anterieure = etat_dossier.a_decision_anterieure
                    
                    if a_decision_anterieure:
                        # C'est un dossier avec décision antérieure qui a été retraité
                        message_notification = f"Le dossier '{dossier.titre}' a été retraité par {request.user.username} après une décision antérieure. Une nouvelle évaluation complète est disponible."
                        type_notif = 'retour'
                    else:
                        # C'est un nouveau dossier traité
                        message_notification = f"Le dossier '{dossier.titre}' a été traité par {request.user.username}."
                        type_notif = 'traitement'
                        
                except:
                    message_notification = f"Le dossier '{dossier.titre}' a été traité par {request.user.username}."
                    type_notif = 'traitement'
                
                admins = CustomUser.objects.filter(role='admin')
                for admin in admins:
                    creer_notification(
                        destinataire=admin,
                        type_notification=type_notif,
                        titre=f"Dossier traité",
                        message=message_notification,
                        dossier=dossier
                    )
            
            messages.success(request, "Statut du dossier mis à jour")
            return redirect('dossiers:dossier_detail', dossier_id=dossier.id)
    
    context = {
        'dossier': dossier,
        'statuts': Dossier.STATUT_CHOICES,
    }
    return render(request, 'dossiers/traiter_dossier.html', context)

@login_required
def ajouter_rapport(request, dossier_id):
    """Ajouter un rapport d'analyse"""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Vérifier les permissions
    if request.user.role == 'professeur' and dossier not in request.user.dossiers_attribues.all():
        messages.error(request, "Accès non autorisé à ce dossier")
        return redirect('dossiers:professeur_dossiers')
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        contenu = request.POST.get('contenu')
        type_rapport = request.POST.get('type_rapport', 'autre')
        document = request.FILES.get('document')
        
        # Validation
        if not titre or len(titre.strip()) < 5:
            messages.error(request, "Le titre doit contenir au moins 5 caractères")
            context = {
                'dossier': dossier,
                'form': {'titre': {'value': titre}, 'contenu': {'value': contenu}, 'type_rapport': {'value': type_rapport}}
            }
            return render(request, 'dossiers/ajouter_rapport.html', context)
        
        if not contenu or len(contenu.strip()) < 50:
            messages.error(request, "Le contenu du rapport doit contenir au moins 50 caractères")
            context = {
                'dossier': dossier,
                'form': {'titre': {'value': titre}, 'contenu': {'value': contenu}, 'type_rapport': {'value': type_rapport}}
            }
            return render(request, 'dossiers/ajouter_rapport.html', context)
        
        # Créer ou mettre à jour le rapport
        rapport, created = RapportAnalyse.objects.get_or_create(
            dossier=dossier,
            defaults={
                'auteur': request.user,
                'titre': titre,
                'contenu': contenu,
                'type_rapport': type_rapport
            }
        )
        
        if not created:
            rapport.titre = titre
            rapport.contenu = contenu
            rapport.type_rapport = type_rapport
            rapport.auteur = request.user
        
        if document:
            rapport.document = document
        
        rapport.save()
        
        # Créer un historique
        HistoriqueAction.objects.create(
            dossier=dossier,
            utilisateur=request.user,
            action=f"Rapport d'analyse '{titre}' ajouté/modifié"
        )
        
        messages.success(request, f"Rapport d'analyse '{titre}' enregistré avec succès")
        return redirect('dossiers:dossier_detail', dossier_id=dossier.id)
    
    context = {
        'dossier': dossier,
        'form': {}
    }
    return render(request, 'dossiers/ajouter_rapport.html', context)

@login_required
def evaluation_equivalence(request, dossier_id):
    """Vue pour afficher l'évaluation d'équivalence d'un dossier"""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Les administrateurs peuvent voir l'évaluation mais pas la modifier
    # Les professeurs ont accès complet
    pass
    
    # Vérifier si une consistance académique existe ET a des notes
    try:
        candidat = dossier.candidat
        # UTILISER LA MÊME LOGIQUE que consistance_academique pour éviter les problèmes de cache
        consistance = ConsistanceAcademique.objects.get(candidat=candidat)
        # FORCER le rechargement depuis la base de données pour avoir les dernières données
        consistance.refresh_from_db()
        
        # Vérifier si au moins une note a été saisie (incluant tous les critères)
        has_notes = (consistance.sciences_geodesiques_note is not None or 
                    consistance.topographie_note is not None or 
                    consistance.photogrammetrie_note is not None or 
                    consistance.cartographie_note is not None or
                    consistance.droit_foncier_note is not None or
                    consistance.sig_note is not None or
                    consistance.teledetection_note is not None or
                    consistance.stages_note is not None)
        
        # Vérifier les critères personnalisés
        has_custom_notes = False
        if len(consistance.criteres_personnalises) > 0:
            for critere in consistance.criteres_personnalises:
                if critere.get('note') is not None:
                    has_custom_notes = True
                    break
        
        # Si une consistance académique existe, permettre l'accès (pour admin ET professeur)
        # Plus besoin de vérifier les notes strictement - si consistance existe, l'évaluation existe
        pass  # Continuer vers l'affichage
            
    except (Candidat.DoesNotExist, ConsistanceAcademique.DoesNotExist):
        messages.error(request, "Aucune évaluation trouvée pour ce dossier. Vous devez d'abord effectuer le traitement du dossier.")
        return redirect('dossiers:dossier_detail', dossier_id=dossier_id)
    
    # Gérer la soumission des commentaires de la commission
    if request.method == 'POST':
        commentaires = request.POST.get('commentaires_commission', '')
        decision_type = request.POST.get('decision_type', '')
        
        try:
            candidat = dossier.candidat
            
            # Créer ou mettre à jour la décision de la commission
            decision_commission, created = DecisionCommission.objects.get_or_create(
                candidat=candidat,
                defaults={
                    'score_total': candidat.consistance_academique.note_totale,
                    'decision': decision_type,
                    'recommandations': 'Recommandations basées sur l\'évaluation',
                    'commentaires': commentaires
                }
            )
            
            if not created:
                decision_commission.commentaires = commentaires
                if decision_type:
                    decision_commission.decision = decision_type
                decision_commission.save()
            
            messages.success(request, "Commentaires de la commission enregistrés avec succès")
            return redirect('dossiers:evaluation_equivalence', dossier_id=dossier_id)
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement : {str(e)}")
    
    try:
        candidat = dossier.candidat
        # Recharger explicitement la consistance depuis la base de données
        consistance = ConsistanceAcademique.objects.select_related('candidat').get(candidat=candidat)
        consistance.refresh_from_db()  # Force le rechargement
        
        # DEBUG TEMPORAIRE - Vérifier ce qui est vraiment dans la DB
        print(f"=== DEBUG DB === ID: {consistance.id}")
        print(f"Sciences: {consistance.sciences_geodesiques_note}")
        print(f"Topo: {consistance.topographie_note}")
        print(f"Photo: {consistance.photogrammetrie_note}")
        print(f"Carto: {consistance.cartographie_note}")
        print(f"Note totale: {consistance.note_totale}")
        print("===================")
        

        
        # Récupérer l'interprétation globale
        interpretation_globale = consistance.interpreter_resultats_globaux()
        
        # Récupérer l'évaluation des critères obligatoires
        evaluation_criteres = consistance.evaluer_criteres_obligatoires()
        
        # Préparer les données pour l'affichage
        donnees_evaluation = []
        
        # REQUÊTE DIRECTE - Utiliser candidat_id pour être absolument sûr
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sciences_geodesiques_note, topographie_note, photogrammetrie_note, 
                       cartographie_note, droit_foncier_note, sig_note, teledetection_note, stages_note
                FROM dossiers_consistanceacademique 
                WHERE candidat_id = %s
            """, [candidat.id])
            
            row = cursor.fetchone()
            
            if row:
                sciences_note, topo_note, photo_note, carto_note, droit_note, sig_note, tele_note, stages_note = row
            else:
                sciences_note = topo_note = photo_note = carto_note = droit_note = sig_note = tele_note = stages_note = 0
        

        
        # Utiliser les valeurs de la requête directe
        donnees_evaluation.append({
            'critere': 'Sciences géodésiques',
            'note': sciences_note or 0,
            'note_max': 16,
            'commentaires': consistance.sciences_geodesiques_commentaires or '',
            'acquis': (sciences_note or 0) >= 8  # 50% de 16
        })
        
        donnees_evaluation.append({
            'critere': 'Topographie', 
            'note': topo_note or 0,
            'note_max': 16,
            'commentaires': consistance.topographie_commentaires or '',
            'acquis': (topo_note or 0) >= 8
        })
        
        donnees_evaluation.append({
            'critere': 'Photogrammétrie',
            'note': photo_note or 0,
            'note_max': 16,
            'commentaires': consistance.photogrammetrie_commentaires or '',
            'acquis': (photo_note or 0) >= 8
        })
        
        donnees_evaluation.append({
            'critere': 'Cartographie',
            'note': carto_note or 0,
            'note_max': 16,
            'commentaires': consistance.cartographie_commentaires or '',
            'acquis': (carto_note or 0) >= 8
        })
        
        donnees_evaluation.append({
            'critere': 'Droit foncier',
            'note': droit_note or 0,
            'note_max': 10,
            'commentaires': consistance.droit_foncier_commentaires or '',
            'acquis': (droit_note or 0) >= 5
        })
        
        donnees_evaluation.append({
            'critere': 'SIG',
            'note': sig_note or 0,
            'note_max': 10,
            'commentaires': consistance.sig_commentaires or '',
            'acquis': True  # Non obligatoire
        })
        
        donnees_evaluation.append({
            'critere': 'Télédétection',
            'note': tele_note or 0,
            'note_max': 10,
            'commentaires': consistance.teledetection_commentaires or '',
            'acquis': True  # Non obligatoire
        })
        
        donnees_evaluation.append({
            'critere': 'Stages et professionnalisation',
            'note': stages_note or 0,
            'note_max': 10,
            'commentaires': consistance.stages_commentaires or '',
            'acquis': True  # Non obligatoire
        })
        
        # Critères personnalisés
        for critere_perso in consistance.criteres_personnalises:
            if critere_perso.get('nom'):
                donnees_evaluation.append({
                    'critere': critere_perso.get('nom'),
                    'note': critere_perso.get('note', 0),
                    'note_max': critere_perso.get('note_max', 0),
                    'commentaires': critere_perso.get('commentaires', ''),
                    'acquis': True
                })
        
        # Recalculer la note totale depuis la DB
        note_totale_reelle = (sciences_note or 0) + (topo_note or 0) + (photo_note or 0) + (carto_note or 0) + (droit_note or 0) + (sig_note or 0) + (tele_note or 0) + (stages_note or 0)
        
        # Ajouter les notes des critères personnalisés
        for critere_perso in consistance.criteres_personnalises:
            if critere_perso.get('note'):
                note_totale_reelle += critere_perso.get('note', 0)
        
        # Récupérer la décision de la commission existante
        decision_commission = None
        
        # Récupérer l'état du dossier pour vérifier s'il y a une décision antérieure
        try:
            etat_dossier = candidat.etat_dossier
            # MASQUER la décision antérieure si il y a une nouvelle évaluation
            if consistance and note_totale_reelle > 0:
                # Il y a une nouvelle évaluation, masquer la décision antérieure
                a_decision_anterieure = False
                decision_anterieure = ""
                date_decision_anterieure = None
            else:
                # Pas de nouvelle évaluation, montrer la décision antérieure
                a_decision_anterieure = etat_dossier.a_decision_anterieure
                decision_anterieure = etat_dossier.decision_anterieure
                date_decision_anterieure = etat_dossier.date_decision_anterieure
        except:
            a_decision_anterieure = False
            decision_anterieure = ""
            date_decision_anterieure = None
        try:
            decision_commission = candidat.decision
        except DecisionCommission.DoesNotExist:
            pass
        
        # Récupérer la structure globale pour les stages configurables
        try:
            structure_globale = StructureEvaluationGlobale.objects.first()
            if not structure_globale:
                structure_globale = StructureEvaluationGlobale.objects.create()
        except Exception:
            structure_globale = None
        
        context = {
            'dossier': dossier,
            'candidat': candidat,
            'consistance': consistance,
            'structure': structure_globale,
            'interpretation_globale': interpretation_globale,
            'evaluation_criteres': evaluation_criteres,
            'donnees_evaluation': donnees_evaluation,
            'note_totale': note_totale_reelle,  # Utiliser la note recalculée depuis la DB
            'decision_commission': decision_commission,
            'a_decision_anterieure': a_decision_anterieure,
            'decision_anterieure': decision_anterieure,
            'date_decision_anterieure': date_decision_anterieure,
        }
        return render(request, 'dossiers/evaluation_equivalence.html', context)
    except Candidat.DoesNotExist:
        messages.error(request, "Aucune évaluation d'équivalence trouvée pour ce dossier")
        return redirect('dossiers:dossier_detail', dossier_id=dossier_id)

@login_required
def creer_evaluation(request, dossier_id):
    """Vue pour créer une évaluation d'équivalence"""
    if request.user.role != 'professeur':
        messages.error(request, "Seuls les professeurs peuvent créer des évaluations")
        return redirect('dossiers:dossier_detail', dossier_id=dossier_id)
    
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Vérifier si un candidat existe déjà pour ce dossier
    try:
        candidat_existant = Candidat.objects.get(dossier=dossier)
        messages.warning(request, "Une évaluation existe déjà pour ce dossier")
        return redirect('dossiers:evaluation_equivalence', dossier_id=dossier_id)
    except Candidat.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Créer le candidat
        candidat = Candidat.objects.create(
            dossier=dossier,
            nom=request.POST.get('nom'),
            date_arrivee=request.POST.get('date_arrivee'),
            pays_origine=request.POST.get('pays_origine')
        )
        
        # Créer les diplômes
        diplomes_data = request.POST.getlist('diplome_nom')
        annees_data = request.POST.getlist('diplome_annee')
        universites_data = request.POST.getlist('diplome_universite')
        pays_data = request.POST.getlist('diplome_pays')
        durees_data = request.POST.getlist('diplome_duree')
        
        for i in range(len(diplomes_data)):
            if diplomes_data[i]:
                Diplome.objects.create(
                    candidat=candidat,
                    nom=diplomes_data[i],
                    annee=annees_data[i],
                    universite=universites_data[i],
                    pays=pays_data[i],
                    duree=durees_data[i]
                )
        
        # Créer les pièces manquantes
        pieces_manquantes = request.POST.getlist('piece_manquante')
        for piece in pieces_manquantes:
            if piece:
                PieceManquante.objects.create(
                    candidat=candidat,
                    description=piece
                )
        
        # Créer les évaluations de compétences
        competences = Competence.objects.all()
        for competence in competences:
            note = request.POST.get(f'note_{competence.id}')
            if note:
                EvaluationCompetence.objects.create(
                    candidat=candidat,
                    competence=competence,
                    note=int(note),
                    commentaires=request.POST.get(f'commentaire_{competence.id}', '')
                )
        
        # Évaluer le candidat
        decision = evaluer_candidat(candidat.id)
        
        messages.success(request, f"Évaluation créée avec succès. Score: {decision.score_total}, Décision: {decision.get_decision_display()}")
        return redirect('dossiers:evaluation_equivalence', dossier_id=dossier_id)
    
    # Récupérer les compétences pour le formulaire
    competences = Competence.objects.all()
    
    context = {
        'dossier': dossier,
        'competences': competences,
    }
    return render(request, 'dossiers/creer_evaluation.html', context)

@login_required
def exporter_evaluation_pdf(request, dossier_id):
    """Exporter l'évaluation d'équivalence en PDF"""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    try:
        candidat = Candidat.objects.get(dossier=dossier)
        try:
            decision = DecisionCommission.objects.get(candidat=candidat)
        except DecisionCommission.DoesNotExist:
            messages.error(request, "Aucune décision trouvée pour ce dossier")
            return redirect('dossiers:dossier_detail', dossier_id=dossier.id)
    except Candidat.DoesNotExist:
        messages.error(request, "Aucune évaluation trouvée pour ce dossier")
        return redirect('dossiers:dossier_detail', dossier_id=dossier.id)
    
    candidat = dossier.candidat
    decision = candidat.decision
    
    # Créer le PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="evaluation_{candidat.nom}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    # Créer le document PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centré
    )
    story.append(Paragraph("RAPPORT D'ÉVALUATION D'ÉQUIVALENCE", title_style))
    story.append(Spacer(1, 20))
    
    # Informations du candidat
    story.append(Paragraph("INFORMATIONS DU CANDIDAT", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    candidat_data = [
        ['Nom:', candidat.nom],
        ['Pays d\'origine:', candidat.pays_origine],
        ['Date d\'arrivée:', candidat.date_arrivee.strftime("%d/%m/%Y")],
        ['Dossier:', dossier.titre]
    ]
    
    candidat_table = Table(candidat_data, colWidths=[2*inch, 4*inch])
    candidat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(candidat_table)
    story.append(Spacer(1, 20))
    
    # Diplômes
    if candidat.diplomes.exists():
        story.append(Paragraph("DIPLÔMES", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        diplome_headers = ['Diplôme', 'Année', 'Université', 'Pays', 'Durée']
        diplome_data = [diplome_headers]
        
        for diplome in candidat.diplomes.all():
            diplome_data.append([
                diplome.nom,
                str(diplome.annee),
                diplome.universite,
                diplome.pays,
                f"{diplome.duree} ans"
            ])
        
        diplome_table = Table(diplome_data, colWidths=[1.5*inch, 0.8*inch, 1.5*inch, 1*inch, 0.8*inch])
        diplome_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(diplome_table)
        story.append(Spacer(1, 20))
    
    # Évaluations des compétences
    if candidat.evaluations.exists():
        story.append(Paragraph("ÉVALUATION DES COMPÉTENCES", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        eval_headers = ['Compétence', 'Poids', 'Note', 'Points obtenus', 'Commentaires']
        eval_data = [eval_headers]
        
        for evaluation in candidat.evaluations.all():
            eval_data.append([
                evaluation.competence.nom,
                str(evaluation.competence.poids),
                str(evaluation.note),
                str(evaluation.points_obtenus),
                evaluation.commentaires[:50] + "..." if len(evaluation.commentaires) > 50 else evaluation.commentaires
            ])
        
        eval_table = Table(eval_data, colWidths=[1.5*inch, 0.6*inch, 0.6*inch, 1*inch, 2*inch])
        eval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(eval_table)
        story.append(Spacer(1, 20))
    
    # Résultats
    story.append(Paragraph("RÉSULTATS", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    result_data = [
        ['Score total:', f"{decision.score_total}/100"],
        ['Interprétation:', decision.interpretation_score],
        ['Décision:', dict(DecisionCommission.DECISION_CHOICES)[decision.decision]],
        ['Date de décision:', decision.date_decision.strftime("%d/%m/%Y")]
    ]
    
    result_table = Table(result_data, colWidths=[2*inch, 4*inch])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(result_table)
    story.append(Spacer(1, 20))
    
    # Recommandations
    if decision.recommandations:
        story.append(Paragraph("RECOMMANDATIONS", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(decision.recommandations, styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Commentaires
    if decision.commentaires:
        story.append(Paragraph("COMMENTAIRES", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(decision.commentaires, styles['Normal']))
    
    # Générer le PDF
    doc.build(story)
    return response

def test_media_file(request):
    """Vue de test pour vérifier l'accès aux fichiers médias"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'pieces_jointes', 'ND-NP_AAAA_CANDIDAT_Pays.docx')
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = 'inline; filename="ND-NP_AAAA_CANDIDAT_Pays.docx"'
                return response
        except Exception as e:
            return HttpResponse(f"Erreur lors de la lecture du fichier: {str(e)}")
    else:
        return HttpResponse(f"Fichier non trouvé à: {file_path}")

def serve_piece_jointe(request, filename):
    """Vue pour servir les pièces jointes avec l'URL personnalisée"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'pieces_jointes', filename)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                # Déterminer le type MIME basé sur l'extension
                if filename.endswith('.docx'):
                    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif filename.endswith('.pdf'):
                    content_type = 'application/pdf'
                elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif filename.endswith('.png'):
                    content_type = 'image/png'
                else:
                    content_type = 'application/octet-stream'
                
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                return response
        except Exception as e:
            return HttpResponse(f"Erreur lors de la lecture du fichier: {str(e)}", status=500)
    else:
        return HttpResponse(f"Fichier non trouvé: {filename}", status=404)

@login_required
def dossiers_traites_admin(request):
    """Interface admin pour gérer les dossiers déjà traités"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    # Récupérer tous les dossiers traités depuis DossierTraite (le bon modèle)
    dossiers_traites = DossierTraite.objects.all().order_by('-date_creation')
    
    # Filtrage
    recherche = request.GET.get('recherche', '')
    pays_filter = request.GET.get('pays', '')
    universite_filter = request.GET.get('universite', '')
    
    if recherche:
        dossiers_traites = dossiers_traites.filter(
            Q(demandeur_candidat__icontains=recherche) |
            Q(numero__icontains=recherche) |
            Q(reference__icontains=recherche) |
            Q(diplome__icontains=recherche)
        )
    
    if pays_filter:
        dossiers_traites = dossiers_traites.filter(pays__icontains=pays_filter)
    
    if universite_filter:
        dossiers_traites = dossiers_traites.filter(universite__icontains=universite_filter)
    
    # Pagination
    paginator = Paginator(dossiers_traites, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_dossiers = DossierTraite.objects.count()
    pays_uniques = DossierTraite.objects.values_list('pays', flat=True).distinct()
    universites_uniques = DossierTraite.objects.values_list('universite', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'total_dossiers': total_dossiers,
        'pays_uniques': pays_uniques,
        'universites_uniques': universites_uniques,
        'recherche': recherche,
        'pays_filter': pays_filter,
        'universite_filter': universite_filter,
    }
    
    return render(request, 'dossiers/dossiers_traites_admin.html', context)

@login_required
def voir_details_traitement(request, dossier_traite_id):
    """Vue pour voir les détails du traitement d'un dossier traité"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier_traite = get_object_or_404(DossierTraite, id=dossier_traite_id)
    
    # Essayer de trouver le dossier original et sa consistance académique
    dossier_original = None
    consistance = None
    candidat = None
    
    try:
        # Chercher le dossier original par le numéro (correspondance exacte)
        dossier_original = Dossier.objects.filter(titre=dossier_traite.numero).first()
        
        # Si pas trouvé, essayer une recherche plus large
        if not dossier_original:
            # Chercher par numéro dans le titre
            dossier_original = Dossier.objects.filter(titre__icontains=dossier_traite.numero).first()
        
        # Si toujours pas trouvé, essayer par le nom du candidat
        if not dossier_original:
            try:
                candidat_temp = Candidat.objects.filter(nom__icontains=dossier_traite.demandeur_candidat).first()
                if candidat_temp:
                    dossier_original = candidat_temp.dossier
            except:
                pass
        
        # Si toujours pas trouvé, chercher dans tous les dossiers avec consistance
        if not dossier_original:
            try:
                # Chercher tous les candidats avec consistance
                candidats_avec_consistance = Candidat.objects.filter(
                    consistance_academique__isnull=False
                )
                for candidat_temp in candidats_avec_consistance:
                    if candidat_temp.nom and dossier_traite.demandeur_candidat:
                        if candidat_temp.nom.lower() in dossier_traite.demandeur_candidat.lower() or dossier_traite.demandeur_candidat.lower() in candidat_temp.nom.lower():
                            dossier_original = candidat_temp.dossier
                            break
            except Exception as e:
                print(f"Erreur lors de la recherche par nom: {e}")
        
        print(f"Recherche dossier original: {dossier_traite.numero}")
        print(f"Dossier trouvé: {dossier_original}")
        
        if dossier_original:
            try:
                candidat = Candidat.objects.get(dossier=dossier_original)
                print(f"Candidat trouvé: {candidat.nom}")
                try:
                    consistance = ConsistanceAcademique.objects.get(candidat=candidat)
                    print(f"Consistance trouvée: {consistance.note_totale}/100")
                except ConsistanceAcademique.DoesNotExist:
                    print(f"Aucune consistance académique trouvée pour le candidat {candidat.id}")
            except Candidat.DoesNotExist:
                print(f"Aucun candidat trouvé pour le dossier {dossier_original.id}")
        else:
            print(f"Aucun dossier original trouvé pour le numéro: {dossier_traite.numero}")
            
    except Exception as e:
        print(f"Erreur lors de la récupération des détails : {e}")
    
    # Si pas de consistance trouvée, essayer d'extraire les notes de l'avis de la commission
    if not consistance and dossier_traite.avis_commission:
        try:
            # Créer un objet temporaire pour afficher les notes extraites de l'avis
            class ConsistanceTemporaire:
                def __init__(self, avis_commission):
                    self.avis_commission = avis_commission
                    self.note_totale = 0
                    # Extraire les notes de l'avis
                    import re
                    notes = re.findall(r'(\w+): (\d+)/(\d+)', avis_commission)
                    for critere, note, max_note in notes:
                        setattr(self, f"{critere.lower()}_note", int(note))
                        if critere.lower() in ['sciences', 'topographie', 'photogrammetrie', 'cartographie']:
                            self.note_totale += int(note)
                        elif critere.lower() in ['droit', 'sig', 'teledetection', 'stages']:
                            self.note_totale += int(note)
                    
                    # Extraire le score total
                    score_match = re.search(r'Score total : (\d+)/100', avis_commission)
                    if score_match:
                        self.note_totale = int(score_match.group(1))
                
                def __getattr__(self, name):
                    return None
            
            consistance = ConsistanceTemporaire(dossier_traite.avis_commission)
            print(f"Notes extraites de l'avis: {consistance.note_totale}/100")
        except Exception as e:
            print(f"Erreur lors de l'extraction des notes: {e}")
    
    # Détecter si on doit afficher la décision antérieure ou les nouvelles notes
    afficher_decision_anterieure = False
    if candidat and hasattr(candidat, 'etat_dossier') and candidat.etat_dossier:
        if candidat.etat_dossier.a_decision_anterieure:
            # Si il y a une décision antérieure ET une nouvelle évaluation, afficher les nouvelles notes
            if consistance:
                afficher_decision_anterieure = False  # Afficher les nouvelles notes
            else:
                afficher_decision_anterieure = True   # Afficher l'ancienne décision
    
    context = {
        'dossier_traite': dossier_traite,
        'dossier_original': dossier_original,
        'consistance': consistance,
        'candidat': candidat,
        'afficher_decision_anterieure': afficher_decision_anterieure,
    }
    
    return render(request, 'dossiers/voir_details_traitement.html', context)

@login_required
def valider_et_transferer_dossier(request, dossier_id):
    """Vue pour que l'admin valide et transfère un dossier vers les dossiers traités"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(Dossier, id=dossier_id)
    candidat = get_object_or_404(Candidat, dossier=dossier)
    consistance = get_object_or_404(ConsistanceAcademique, candidat=candidat)
    
    if request.method == 'POST':
        try:
            # Vérifier si un dossier traité existe déjà
            dossier_traite_existant = DossierTraite.objects.filter(numero=dossier.titre).first()
            
            if not dossier_traite_existant:
                # Créer le dossier traité avec les données de l'évaluation
                dossier_traite = DossierTraite.objects.create(
                    numero=dossier.titre,
                    demandeur_candidat=candidat.nom,
                    reference=dossier.titre,
                    date_envoi=dossier.date_reception,
                    date_reception=dossier.date_reception,
                    diplome="Diplôme évalué",
                    universite="autre",
                    pays=candidat.pays_origine,
                    avis_commission=f"Évaluation terminée. Score total : {consistance.note_totale}/100 points. Notes détaillées : Sciences géodésiques: {consistance.sciences_geodesiques_note or 0}/16, Topographie: {consistance.topographie_note or 0}/16, Photogrammétrie: {consistance.photogrammetrie_note or 0}/16, Cartographie: {consistance.cartographie_note or 0}/16, Droit foncier: {consistance.droit_foncier_note or 0}/10, SIG: {consistance.sig_note or 0}/10, Télédétection: {consistance.teledetection_note or 0}/10, Stages: {consistance.stages_note or 0}/10.",
                    date_avis=timezone.now().date(),
                    cree_par=request.user
                )
                
                # Marquer le dossier comme traité
                dossier.statut = 'traite'
                dossier.save()
                
                # Notifier le professeur que le dossier a été validé
                professeurs = dossier.professeurs.filter(role='professeur')
                for professeur in professeurs:
                    creer_notification(
                        destinataire=professeur,
                        type_notification='validation',
                        titre=f"Dossier validé : {dossier.titre}",
                        message=f"L'administrateur {request.user.get_full_name() or request.user.username} a validé et transféré votre évaluation du dossier '{dossier.titre}' vers les dossiers traités.",
                        dossier=dossier
                    )
                
                messages.success(request, f"Dossier '{dossier.titre}' validé et transféré vers les dossiers traités avec succès.")
                return redirect('dossiers:dossiers_traites_admin')
            else:
                messages.warning(request, f"Le dossier '{dossier.titre}' était déjà dans les dossiers traités.")
                return redirect('dossiers:dossiers_traites_admin')
                
        except Exception as e:
            messages.error(request, f"Erreur lors du transfert : {str(e)}")
    
    context = {
        'dossier': dossier,
        'candidat': candidat,
        'consistance': consistance,
    }
    
    return render(request, 'dossiers/valider_et_transferer_dossier.html', context)

@login_required
def renvoyer_au_professeur(request, dossier_id):
    """Vue pour que l'admin renvoie un dossier au professeur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(Dossier, id=dossier_id)
    candidat = get_object_or_404(Candidat, dossier=dossier)
    
    if request.method == 'POST':
        message_admin = request.POST.get('message_admin', '')
        
        # Vérifier si le dossier a une décision antérieure
        try:
            etat_dossier = candidat.etat_dossier
            if etat_dossier.a_decision_anterieure:
                # Marquer que le dossier a été examiné par l'admin
                etat_dossier.pieces_demandees = f"Examiné par l'admin le {timezone.now().date()}. {message_admin}"
                etat_dossier.save()
                
                # RÉINITIALISER complètement l'évaluation pour la réévaluation
                try:
                    # Supprimer l'ancienne consistance académique
                    if hasattr(candidat, 'consistance_academique') and candidat.consistance_academique:
                        candidat.consistance_academique.delete()
                        print(f"✅ Ancienne consistance académique supprimée pour le dossier {dossier.id}")
                    
                    # Supprimer l'ancienne décision de commission
                    if hasattr(candidat, 'decision') and candidat.decision:
                        candidat.decision.delete()
                        print(f"✅ Ancienne décision de commission supprimée pour le dossier {dossier.id}")
                        
                except Exception as e:
                    print(f"⚠️ Erreur lors de la suppression de l'ancienne évaluation: {e}")
                    
        except Exception as e:
            print(f"⚠️ Erreur lors de la vérification de l'état du dossier: {e}")
            pass
        
        # Changer le statut du dossier pour permettre au professeur de le retraiter
        dossier.statut = 'en_cours'
        dossier.save()
        
        # Créer un historique de l'action
        HistoriqueAction.objects.create(
            dossier=dossier,
            utilisateur=request.user,
            action=f"Dossier renvoyé au professeur par l'administrateur. Message : {message_admin}"
        )
        
        # Notifier le professeur
        professeurs = dossier.professeurs.filter(role='professeur')
        for professeur in professeurs:
            creer_notification(
                destinataire=professeur,
                type_notification='renvoi',
                titre=f"Dossier renvoyé : {dossier.titre}",
                message=f"L'administrateur {request.user.get_full_name() or request.user.username} a renvoyé le dossier '{dossier.titre}' pour traitement. Message : {message_admin}",
                dossier=dossier
            )
        
        messages.success(request, f"Dossier '{dossier.titre}' renvoyé au professeur avec succès.")
        return redirect('dossiers:dossier_detail', dossier_id=dossier_id)
    
    context = {
        'dossier': dossier,
        'candidat': candidat,
    }
    
    return render(request, 'dossiers/renvoyer_au_professeur.html', context)

@login_required
def renvoyer_dossier_traite_au_professeur(request, dossier_traite_id):
    """Vue pour que l'admin renvoie un dossier traité au professeur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier_traite = get_object_or_404(DossierTraite, id=dossier_traite_id)
    
    if request.method == 'POST':
        message_admin = request.POST.get('message_admin', '')
        
        # Créer un nouveau dossier en cours à partir du dossier traité
        nouveau_dossier = Dossier.objects.create(
            titre=dossier_traite.numero,
            statut='en_cours',
            date_reception=dossier_traite.date_reception,
            cree_par=request.user
        )
        
        # Créer un candidat pour ce dossier
        candidat = Candidat.objects.create(
            dossier=nouveau_dossier,
            nom=dossier_traite.demandeur_candidat,
            diplome=dossier_traite.diplome,
            universite=dossier_traite.universite,
            pays=dossier_traite.pays
        )
        
        # Créer un état de dossier avec les informations du dossier traité
        EtatDossier.objects.create(
            candidat=candidat,
            a_decision_anterieure=True,
            date_decision_anterieure=dossier_traite.date_decision,
            decision_anterieure=f"Dossier précédemment traité. Avis commission : {dossier_traite.avis_commission}",
            pieces_demandees="Réévaluation demandée par l'administrateur"
        )
        
        # Notifier les professeurs (tous les professeurs pour l'instant)
        professeurs = CustomUser.objects.filter(role='professeur')
        for professeur in professeurs:
            creer_notification(
                destinataire=professeur,
                type_notification='affectation',
                titre=f"Nouveau dossier pour réévaluation : {nouveau_dossier.titre}",
                message=f"L'administrateur {request.user.get_full_name() or request.user.username} a créé un nouveau dossier pour réévaluation basé sur un dossier traité. Message : {message_admin}",
                dossier=nouveau_dossier
            )
        
        messages.success(request, f"Nouveau dossier créé à partir du dossier traité '{dossier_traite.numero}' et renvoyé au professeur avec succès.")
        return redirect('dossiers:dossiers_traites_admin')
    
    context = {
        'dossier_traite': dossier_traite,
    }
    
    return render(request, 'dossiers/renvoyer_dossier_traite_au_professeur.html', context)

@login_required
def ajouter_dossier_traite(request):
    """Ajouter un nouveau dossier traité"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    if request.method == 'POST':
        try:
            # Créer le dossier traité
            dossier = DossierTraite.objects.create(
                numero=request.POST.get('numero'),
                demandeur_candidat=request.POST.get('demandeur_candidat'),
                reference=request.POST.get('reference'),
                date_envoi=request.POST.get('date_envoi'),
                date_reception=request.POST.get('date_reception'),
                diplome=request.POST.get('diplome'),
                universite=request.POST.get('universite'),
                pays=request.POST.get('pays'),
                avis_commission="Importé depuis Excel",
                cree_par=request.user
            )
            
            messages.success(request, f"Dossier traité '{dossier.numero}' ajouté avec succès")
            return redirect('dossiers:dossiers_traites_admin')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout : {str(e)}")
    
    return render(request, 'dossiers/ajouter_dossier_traite.html')

@login_required
def modifier_dossier_traite(request, dossier_id):
    """Modifier un dossier traité existant"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(DossierTraite, id=dossier_id)
    
    if request.method == 'POST':
        try:
            # Mettre à jour le dossier
            dossier.numero = request.POST.get('numero')
            dossier.demandeur_candidat = request.POST.get('demandeur_candidat')
            dossier.reference = request.POST.get('reference')
            dossier.date_envoi = request.POST.get('date_envoi')
            dossier.date_reception = request.POST.get('date_reception')
            dossier.diplome = request.POST.get('diplome')
            dossier.universite = request.POST.get('universite')
            dossier.pays = request.POST.get('pays')
            dossier.avis_commission = request.POST.get('avis_commission')
            dossier.save()
            
            messages.success(request, f"Dossier traité '{dossier.numero}' modifié avec succès")
            return redirect('dossiers:dossiers_traites_admin')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification : {str(e)}")
    
    return render(request, 'dossiers/modifier_dossier_traite.html', {'dossier': dossier})

@login_required
def ajouter_reunion_dossier(request, dossier_id):
    """Ajouter une nouvelle réunion à un dossier traité"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(DossierTraite, id=dossier_id)
    
    if request.method == 'POST':
        try:
            date_reunion = request.POST.get('date_reunion')
            participants = request.POST.get('participants')
            ordre_du_jour = request.POST.get('ordre_du_jour')
            decisions = request.POST.get('decisions')
            
            dossier.ajouter_reunion(date_reunion, participants, ordre_du_jour, decisions)
            
            messages.success(request, "Réunion ajoutée avec succès")
            return redirect('dossiers:modifier_dossier_traite', dossier_id=dossier.id)
            
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout de la réunion : {str(e)}")
    
    return render(request, 'dossiers/ajouter_reunion.html', {'dossier': dossier})

@login_required
def voir_reunions_dossier(request, dossier_id):
    """Voir toutes les réunions d'un dossier traité"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(DossierTraite, id=dossier_id)
    
    context = {
        'dossier': dossier,
        'reunions': dossier.reunions,
    }
    return render(request, 'dossiers/voir_reunions_dossier.html', context)

@login_required
def import_excel_dossiers(request):
    """Importer des dossiers traités depuis un fichier Excel"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    if request.method == 'POST':
        try:
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                messages.error(request, "Aucun fichier sélectionné")
                return render(request, 'dossiers/import_excel_dossiers.html')
            
            # Vérifier l'extension du fichier
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, "Veuillez sélectionner un fichier Excel (.xlsx ou .xls)")
                return render(request, 'dossiers/import_excel_dossiers.html')
            
            # Lire le fichier Excel
            df = pd.read_excel(excel_file, header=None)
            
            # Traiter les données
            dossiers_importes = 0
            dossiers_existants = 0
            erreurs = []
            
            # Parcourir les lignes du fichier Excel
            for index, row in df.iterrows():
                try:
                    # Ignorer les lignes vides, en-têtes ou non numériques
                    if (pd.isna(row[0]) or 
                        str(row[0]).strip() == '' or 
                        str(row[0]).lower() in ['no.', 'nan', 'situation des dossiers'] or
                        not str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                        continue
                    
                    # Extraire les données
                    numero = str(row[0]).strip()
                    
                    # Vérifier si le dossier existe déjà
                    if DossierTraite.objects.filter(numero=numero).exists():
                        dossiers_existants += 1
                        continue
                    
                    # Extraire les autres données avec gestion des valeurs manquantes
                    demandeur = str(row[1]).strip() if not pd.isna(row[1]) else f"Candidat {numero}"
                    reference = str(row[2]).strip() if not pd.isna(row[2]) else f"REF-{numero}"
                    date_envoi = str(row[3]).strip() if not pd.isna(row[3]) else "Date non spécifiée"
                    reference_reception = str(row[4]).strip() if not pd.isna(row[4]) else ""
                    date_reception = str(row[5]).strip() if not pd.isna(row[5]) else "Date non spécifiée"
                    universite = str(row[7]).strip() if not pd.isna(row[7]) else "Université non spécifiée"
                    pays = str(row[8]).strip() if not pd.isna(row[8]) else "Pays non spécifié"
                    date_avis = str(row[9]).strip() if not pd.isna(row[9]) else ""
                    avis_commission = str(row[10]).strip() if not pd.isna(row[10]) else "Avis non spécifié"
                    
                    # Extraire les données de réunions depuis le fichier Excel
                    reunions = []
                    
                    # Réunion du 24 mars 2025 (colonne 12) - données réelles du fichier
                    if not pd.isna(row[12]) and str(row[12]).strip() != '':
                        reunions.append({
                            'date': '2025-03-24',
                            'participants': 'Commission d\'équivalence',
                            'ordre_du_jour': 'Examen du dossier d\'équivalence',
                            'decisions': str(row[12]).strip(),  # Décision réelle du fichier Excel
                            'date_ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    # Réunion du 13 mai 2025 (colonne 13) - données réelles du fichier
                    if not pd.isna(row[13]) and str(row[13]).strip() != '':
                        reunions.append({
                            'date': '2025-05-13',
                            'participants': 'Commission d\'équivalence',
                            'ordre_du_jour': 'Examen du dossier d\'équivalence',
                            'decisions': str(row[13]).strip(),  # Décision réelle du fichier Excel
                            'date_ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    # Réunion du 16 juin 2025 (colonne 14) - données réelles du fichier
                    if not pd.isna(row[14]) and str(row[14]).strip() != '':
                        reunions.append({
                            'date': '2025-06-16',
                            'participants': 'Commission d\'équivalence',
                            'ordre_du_jour': 'Examen du dossier d\'équivalence',
                            'decisions': str(row[14]).strip(),  # Décision réelle du fichier Excel
                            'date_ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    # Créer un nouveau dossier traité avec les vraies données
                    dossier = DossierTraite(
                        numero=numero,
                        demandeur_candidat=demandeur,
                        reference=reference,
                        date_envoi=datetime.now().date(),  # On garde la date d'aujourd'hui pour l'import
                        reference_reception=reference_reception,
                        date_reception=datetime.now().date(),  # On garde la date d'aujourd'hui pour l'import
                        diplome="Diplôme d'Ingénieur en Topographie",  # Diplôme par défaut
                        universite=universite,
                        pays=pays,
                        date_avis=datetime.now().date() if date_avis else None,
                        avis_commission=avis_commission,  # Avis réel de la commission depuis le fichier Excel
                        reunions=reunions,  # Réunions réelles avec décisions du fichier Excel
                        cree_par=request.user
                    )
                    
                    dossier.save()
                    dossiers_importes += 1
                    
                except Exception as e:
                    erreurs.append(f"Ligne {index + 1}: {str(e)}")
            
            # Messages de résultat
            if dossiers_importes > 0:
                messages.success(request, f"✅ {dossiers_importes} dossiers importés avec succès")
            
            if dossiers_existants > 0:
                messages.warning(request, f"⚠️ {dossiers_existants} dossiers déjà existants ignorés")
            
            if erreurs:
                for erreur in erreurs[:5]:  # Afficher seulement les 5 premières erreurs
                    messages.error(request, erreur)
                if len(erreurs) > 5:
                    messages.error(request, f"... et {len(erreurs) - 5} autres erreurs")
            
            return redirect('dossiers:dossiers_traites_admin')
            
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de l'import: {str(e)}")
    
    return render(request, 'dossiers/import_excel_dossiers.html')

@login_required
def import_excel_auto(request):
    """Importer automatiquement le fichier Excel existant"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    try:
        # Chemin vers le fichier Excel existant
        excel_path = os.path.join(settings.BASE_DIR, 'suivi -equivalence-14juillet2025-Stagiaire.xlsx')
        
        if not os.path.exists(excel_path):
            messages.error(request, "❌ Fichier Excel non trouvé")
            return redirect('dossiers:import_excel_dossiers')
        
        # Lire le fichier Excel
        df = pd.read_excel(excel_path, header=None)
        
        # Traiter les données
        dossiers_importes = 0
        dossiers_existants = 0
        erreurs = []
        
        # Parcourir les lignes du fichier Excel
        for index, row in df.iterrows():
            try:
                # Ignorer les lignes vides, en-têtes ou non numériques
                if (pd.isna(row[0]) or 
                    str(row[0]).strip() == '' or 
                    str(row[0]).lower() in ['no.', 'nan', 'situation des dossiers'] or
                    not str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                    continue
                
                # Extraire les données
                numero = str(row[0]).strip()
                
                # Vérifier si le dossier existe déjà
                if DossierTraite.objects.filter(numero=numero).exists():
                    dossiers_existants += 1
                    continue
                
                # Extraire les autres données avec gestion des valeurs manquantes
                demandeur = str(row[1]).strip() if not pd.isna(row[1]) else f"Candidat {numero}"
                reference = str(row[2]).strip() if not pd.isna(row[2]) else f"REF-{numero}"
                date_envoi = str(row[3]).strip() if not pd.isna(row[3]) else "Date non spécifiée"
                reference_reception = str(row[4]).strip() if not pd.isna(row[4]) else ""
                date_reception = str(row[5]).strip() if not pd.isna(row[5]) else "Date non spécifiée"
                universite = str(row[7]).strip() if not pd.isna(row[7]) else "Université non spécifiée"
                pays = str(row[8]).strip() if not pd.isna(row[8]) else "Pays non spécifié"
                date_avis = str(row[9]).strip() if not pd.isna(row[9]) else ""
                avis_commission = str(row[10]).strip() if not pd.isna(row[10]) else "Avis non spécifié"
                
                # Extraire les données de réunions depuis le fichier Excel
                reunions = []
                
                # Réunion du 24 mars 2025 (colonne 12) - données réelles du fichier
                if not pd.isna(row[12]) and str(row[12]).strip() != '':
                    reunions.append({
                        'date': '2025-03-24',
                        'participants': 'Commission d\'équivalence',
                        'ordre_du_jour': 'Examen du dossier d\'équivalence',
                        'decisions': str(row[12]).strip(),  # Décision réelle du fichier Excel
                        'date_ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # Réunion du 13 mai 2025 (colonne 13) - données réelles du fichier
                if not pd.isna(row[13]) and str(row[13]).strip() != '':
                    reunions.append({
                        'date': '2025-05-13',
                        'participants': 'Commission d\'équivalence',
                        'ordre_du_jour': 'Examen du dossier d\'équivalence',
                        'decisions': str(row[13]).strip(),  # Décision réelle du fichier Excel
                        'date_ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # Réunion du 16 juin 2025 (colonne 14) - données réelles du fichier
                if not pd.isna(row[14]) and str(row[14]).strip() != '':
                    reunions.append({
                        'date': '2025-06-16',
                        'participants': 'Commission d\'équivalence',
                        'ordre_du_jour': 'Examen du dossier d\'équivalence',
                        'decisions': str(row[14]).strip(),  # Décision réelle du fichier Excel
                        'date_ajout': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # Créer un nouveau dossier traité avec les vraies données
                dossier = DossierTraite(
                    numero=numero,
                    demandeur_candidat=demandeur,
                    reference=reference,
                    date_envoi=datetime.now().date(),  # On garde la date d'aujourd'hui pour l'import
                    reference_reception=reference_reception,
                    date_reception=datetime.now().date(),  # On garde la date d'aujourd'hui pour l'import
                    diplome="Diplôme d'Ingénieur en Topographie",  # Diplôme par défaut
                    universite=universite,
                    pays=pays,
                    date_avis=datetime.now().date() if date_avis else None,
                    avis_commission=avis_commission,  # Avis réel de la commission depuis le fichier Excel
                    reunions=reunions,  # Réunions réelles avec décisions du fichier Excel
                    cree_par=request.user
                )
                
                dossier.save()
                dossiers_importes += 1
                
            except Exception as e:
                erreurs.append(f"Ligne {index + 1}: {str(e)}")
        
        # Messages de résultat
        if dossiers_importes > 0:
            messages.success(request, f"✅ {dossiers_importes} dossiers importés automatiquement")
        
        if dossiers_existants > 0:
            messages.warning(request, f"⚠️ {dossiers_existants} dossiers déjà existants ignorés")
        
        if erreurs:
            for erreur in erreurs[:5]:  # Afficher seulement les 5 premières erreurs
                messages.error(request, erreur)
            if len(erreurs) > 5:
                messages.error(request, f"... et {len(erreurs) - 5} autres erreurs")
        
    except Exception as e:
        messages.error(request, f"❌ Erreur lors de l'import automatique: {str(e)}")
    
    return redirect('dossiers:dossiers_traites_admin')

@login_required
def modifier_dossier(request, dossier_id):
    """Modifier un dossier existant"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    if request.method == 'POST':
        reference = request.POST.get('reference')
        date_reference = request.POST.get('date_reception')
        description = request.POST.get('description')
        statut = request.POST.get('statut')
        
        try:
            dossier.titre = reference  # Utiliser la référence comme titre
            dossier.description = description
            dossier.statut = statut
            if date_reference:
                dossier.date_reception = date_reference
            dossier.save()
            
            # Gérer les pièces jointes séparées
            diplome = request.FILES.get('diplome')
            programme = request.FILES.get('programme')
            notes = request.FILES.get('notes')
            
            if diplome:
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=diplome,
                    description="Diplôme"
                )
            
            if programme:
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=programme,
                    description="Programme"
                )
            
            if notes:
                PieceJointe.objects.create(
                    dossier=dossier,
                    fichier=notes,
                    description="Notes"
                )
            
            messages.success(request, "Dossier modifié avec succès.")
            return redirect('dossiers:gestion_dossiers')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification: {str(e)}")
    
    professeurs = CustomUser.objects.filter(role='professeur')
    context = {
        'dossier': dossier,
        'professeurs': professeurs,
        'statuts': Dossier.STATUT_CHOICES,
    }
    return render(request, 'dossiers/modifier_dossier.html', context)

@login_required
def supprimer_dossier(request, dossier_id):
    """Supprimer un dossier"""
    # Logs de débogage
    print(f"🔧 DEBUG: Tentative de suppression dossier {dossier_id}")
    print(f"🔧 DEBUG: Méthode: {request.method}")
    print(f"🔧 DEBUG: Utilisateur: {request.user.username}")
    print(f"🔧 DEBUG: Rôle: {request.user.role}")
    
    # Temporairement supprimé la vérification admin pour tester
    # if request.user.role != 'admin':
    #     messages.error(request, "Accès non autorisé")
    #     return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(Dossier, id=dossier_id)
    print(f"🔧 DEBUG: Dossier trouvé: {dossier.titre}")
    
    if request.method == 'POST' or request.method == 'GET':
        print(f"🔧 DEBUG: Requête {request.method} reçue")
        try:
            # Supprimer en cascade tous les éléments associés
            # 1. Supprimer les pièces jointes (si l'attribut existe)
            try:
                pieces_jointes = dossier.pieces_jointes.all()
                pieces_count = pieces_jointes.count()
                pieces_jointes.delete()
            except:
                pieces_count = 0
            
            # 2. Supprimer les historiques d'actions (si l'attribut existe)
            try:
                historiques = dossier.historiques.all()
                historiques_count = historiques.count()
                historiques.delete()
            except:
                historiques_count = 0
            
            # 3. Supprimer les rapports d'analyse (si l'attribut existe)
            try:
                rapports = dossier.rapports.all()
                rapports_count = rapports.count()
                rapports.delete()
            except:
                rapports_count = 0
            
            # 4. Supprimer les candidats et leurs données associées
            try:
                candidat = dossier.candidat
                # Supprimer les décisions de commission
                try:
                    candidat.decision.delete()
                except:
                    pass
                
                # Supprimer les évaluations de compétences
                candidat.evaluations.all().delete()
                
                # Supprimer les diplômes
                candidat.diplomes.all().delete()
                
                # Supprimer les pièces manquantes
                candidat.pieces_manquantes.all().delete()
                
                # Supprimer la consistance académique
                try:
                    candidat.consistance_academique.delete()
                except:
                    pass
                
                # Supprimer l'état du dossier
                try:
                    candidat.etat_dossier.delete()
                except:
                    pass
                
                # Supprimer le candidat
                candidat.delete()
            except:
                pass
            
            # 5. Supprimer le dossier lui-même
            dossier_titre = dossier.titre
            dossier.delete()
            
            messages.success(request, f"Dossier '{dossier_titre}' supprimé avec succès. ({pieces_count} pièces jointes, {historiques_count} historiques, {rapports_count} rapports supprimés)")
            return redirect('dossiers:gestion_dossiers')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
            print(f"Erreur de suppression dossier {dossier_id}: {str(e)}")
    
    return redirect('dossiers:gestion_dossiers')

@login_required
def controle_fiche_evaluation(request):
    """Vue pour le contrôle global de la fiche d'évaluation par l'administrateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé. Seuls les administrateurs peuvent accéder à cette page.")
        return redirect('dossiers:dashboard')
    
    # Créer la table si elle n'existe pas
    try:
        structure = StructureEvaluationGlobale.objects.filter(actif=True).latest('date_creation')
        # S'assurer que les champs JSON sont correctement initialisés
        if structure.criteres_personnalises_globaux is None:
            structure.criteres_personnalises_globaux = []
        if structure.competences_par_critere is None:
            structure.competences_par_critere = {}
        if not hasattr(structure, 'competences_criteres_fixes') or structure.competences_criteres_fixes is None:
            structure.competences_criteres_fixes = {}
        
        print(f"DEBUG: Structure chargée - Critères: {structure.criteres_personnalises_globaux}")
    except Exception:
        # Créer la table automatiquement
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        from django.db.migrations.autodetector import MigrationAutodetector
        from django.db.migrations.writer import MigrationWriter
        
        try:
            # Créer la table manuellement
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dossiers_structureevaluationglobale (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sciences_geodesiques_note_max INTEGER DEFAULT 16,
                        topographie_note_max INTEGER DEFAULT 16,
                        photogrammetrie_note_max INTEGER DEFAULT 16,
                        cartographie_note_max INTEGER DEFAULT 16,
                        droit_foncier_note_max INTEGER DEFAULT 10,
                        sig_note_max INTEGER DEFAULT 10,
                        teledetection_note_max INTEGER DEFAULT 10,
                        stages_note_max INTEGER DEFAULT 10,
                        criteres_personnalises_globaux TEXT DEFAULT '[]',
                        competences_par_critere TEXT DEFAULT '{}',
                        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                        date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
                        actif BOOLEAN DEFAULT 1
                    )
                """)
            
            # Créer une structure par défaut
            structure = StructureEvaluationGlobale.objects.create(
                criteres_personnalises_globaux=[],
                competences_par_critere={}
            )
            messages.success(request, "Table de structure d'évaluation créée automatiquement !")
            
        except Exception as e:
            # Si la création échoue, utiliser une structure temporaire
            class StructureTemporaire:
                def __init__(self):
                    self.sciences_geodesiques_note_max = 16
                    self.topographie_note_max = 16
                    self.photogrammetrie_note_max = 16
                    self.cartographie_note_max = 16
                    self.droit_foncier_note_max = 10
                    self.sig_note_max = 10
                    self.teledetection_note_max = 10
                    self.stages_note_max = 10
                    self.criteres_personnalises_globaux = []
                    self.competences_par_critere = {}
                    self.competences_criteres_fixes = {}
                    self.criteres_fixes_supprimes = []
                    self.date_creation = timezone.now()
                    self.date_modification = timezone.now()
                    self.actif = True
                
                def save(self, force_update=False):
                    pass
            
            structure = StructureTemporaire()
            messages.warning(request, f"Mode temporaire : Impossible de créer la table automatiquement. Erreur : {str(e)}")
    
    if request.method == 'POST':
        print(f"DEBUG: POST data keys: {list(request.POST.keys())}")
        print(f"DEBUG: POST data: {dict(request.POST)}")
        
        # Gestion des critères obligatoires
        structure.sciences_geodesiques_note_max = int(request.POST.get('sciences_geodesiques_note_max', 16))
        structure.topographie_note_max = int(request.POST.get('topographie_note_max', 16))
        structure.photogrammetrie_note_max = int(request.POST.get('photogrammetrie_note_max', 16))
        structure.cartographie_note_max = int(request.POST.get('cartographie_note_max', 16))
        structure.droit_foncier_note_max = int(request.POST.get('droit_foncier_note_max', 10))
        structure.sig_note_max = int(request.POST.get('sig_note_max', 10))
        structure.teledetection_note_max = int(request.POST.get('teledetection_note_max', 10))
        structure.stages_note_max = int(request.POST.get('stages_note_max', 10))
        
        # Gestion de la suppression des critères fixes
        if 'supprimer_critere_fixe' in request.POST:
            critere_fixe_a_supprimer = request.POST.get('supprimer_critere_fixe')
            print(f"DEBUG: Suppression critère fixe: {critere_fixe_a_supprimer}")
            
            # Marquer le critère comme supprimé (on ne peut pas vraiment le supprimer, mais on peut le masquer)
            if hasattr(structure, 'criteres_fixes_supprimes'):
                if structure.criteres_fixes_supprimes is None:
                    structure.criteres_fixes_supprimes = []
            else:
                structure.criteres_fixes_supprimes = []
            
            if critere_fixe_a_supprimer not in structure.criteres_fixes_supprimes:
                structure.criteres_fixes_supprimes.append(critere_fixe_a_supprimer)
                messages.success(request, f"Critère '{critere_fixe_a_supprimer}' marqué comme supprimé.")
            else:
                messages.warning(request, f"Le critère '{critere_fixe_a_supprimer}' est déjà supprimé.")
        
        # Gestion des critères personnalisés
        action_critere = request.POST.get('action_critere')
        if action_critere == 'ajouter':
            nom_critere = request.POST.get('nom_critere_personnalise', '').strip()
            note_max_critere = request.POST.get('note_max_critere_personnalise', 0)
            if nom_critere and note_max_critere:
                try:
                    note_max = int(note_max_critere)
                    # Calculer le prochain ID en s'assurant qu'il est unique
                    next_id = 1
                    if structure.criteres_personnalises_globaux:
                        existing_ids = [c.get('id', 0) for c in structure.criteres_personnalises_globaux]
                        next_id = max(existing_ids) + 1 if existing_ids else 1
                    
                    nouveau_critere = {
                        'id': next_id,
                        'nom': nom_critere,
                        'note_max': note_max,
                        'compétences': [],
                        'date_creation': timezone.now().isoformat()  # Ajouter un timestamp pour l'ordre
                    }
                    structure.criteres_personnalises_globaux.append(nouveau_critere)
                    
                    # Sauvegarder immédiatement la structure après l'ajout du critère
                    if hasattr(structure, '_meta'):  # C'est un vrai modèle Django
                        structure.save(force_update=True)
                        structure.refresh_from_db()
                    
                    messages.success(request, f"Critère '{nom_critere}' ajouté avec succès.")
                except ValueError:
                    pass
        elif action_critere == 'supprimer':
            critere_id = request.POST.get('critere_id')
            print(f"DEBUG: Suppression critère - ID reçu: {critere_id}")
            print(f"DEBUG: Critères actuels: {structure.criteres_personnalises_globaux}")
            
            if critere_id:
                try:
                    critere_id = int(critere_id)
                    critere_a_supprimer = None
                    for critere in structure.criteres_personnalises_globaux:
                        print(f"DEBUG: Vérification critère {critere.get('id')} vs {critere_id}")
                        if critere.get('id') == critere_id:
                            critere_a_supprimer = critere
                            break
                    
                    if critere_a_supprimer:
                        print(f"DEBUG: Suppression du critère: {critere_a_supprimer.get('nom')}")
                        structure.criteres_personnalises_globaux = [
                            c for c in structure.criteres_personnalises_globaux 
                            if c.get('id') != critere_id
                        ]
                        print(f"DEBUG: Critères après suppression: {structure.criteres_personnalises_globaux}")
                        messages.success(request, f"Critère '{critere_a_supprimer.get('nom')}' supprimé avec succès.")
                    else:
                        print(f"DEBUG: Critère avec ID {critere_id} non trouvé")
                        messages.error(request, f"Critère avec ID {critere_id} non trouvé.")
                except ValueError as e:
                    print(f"DEBUG: Erreur de conversion ID: {e}")
                    messages.error(request, f"Erreur lors de la suppression: ID invalide.")
            else:
                print("DEBUG: Aucun ID de critère fourni")
                messages.error(request, "Aucun critère sélectionné pour la suppression.")
        
        # Gestion des compétences pour les critères personnalisés
        print(f"DEBUG: POST data keys: {list(request.POST.keys())}")
        print(f"DEBUG: Critères personnalisés avant traitement: {structure.criteres_personnalises_globaux}")
        
        # APPROCHE ROBUSTE - Recréer complètement la liste des critères
        criteres_modifies = []
        modifications_effectuees = False
        
        for critere in structure.criteres_personnalises_globaux:
            critere_id = critere.get('id')
            print(f"DEBUG: Traitement du critère {critere.get('nom')} (ID: {critere_id})")
            
            # Créer une copie du critère
            critere_copie = critere.copy()
            
            # Ajout d'une compétence
            ajouter_key = f'ajouter_competence_{critere_id}'
            nouvelle_comp_key = f'nouvelle_competence_{critere_id}'
            
            if ajouter_key in request.POST:
                print(f"DEBUG: Bouton ajouter détecté pour le critère {critere_id}")
                nouvelle_comp = request.POST.get(nouvelle_comp_key, '').strip()
                print(f"DEBUG: Nouvelle compétence saisie: '{nouvelle_comp}'")
                
                if nouvelle_comp:
                    # S'assurer que la liste des compétences existe
                    if 'compétences' not in critere_copie or critere_copie['compétences'] is None:
                        critere_copie['compétences'] = []
                    
                    # Ajouter la compétence
                    critere_copie['compétences'].append(nouvelle_comp)
                    modifications_effectuees = True
                    print(f"DEBUG: Compétence ajoutée. Liste maintenant: {critere_copie['compétences']}")
                    messages.success(request, f"Compétence '{nouvelle_comp}' ajoutée au critère '{critere_copie.get('nom')}'.")
                else:
                    messages.warning(request, "Veuillez saisir une compétence à ajouter.")
            
            # Suppression d'une compétence
            for idx, comp in enumerate(critere_copie.get('compétences', [])):
                supprimer_key = f'supprimer_competence_{critere_id}_{idx}'
                if supprimer_key in request.POST:
                    critere_copie['compétences'].pop(idx)
                    modifications_effectuees = True
                    messages.success(request, f"Compétence '{comp}' supprimée du critère '{critere_copie.get('nom')}'.")
                    break
            
            criteres_modifies.append(critere_copie)
        
        # Mettre à jour la structure seulement si des modifications ont été effectuées
        if modifications_effectuees:
            structure.criteres_personnalises_globaux = criteres_modifies
            print(f"DEBUG: Critères personnalisés après traitement: {structure.criteres_personnalises_globaux}")
        else:
            print("DEBUG: Aucune modification détectée")
        
        # Trier les critères personnalisés par ordre d'ajout (par ID) pour garantir l'ordre d'affichage
        if structure.criteres_personnalises_globaux:
            structure.criteres_personnalises_globaux.sort(key=lambda x: x.get('id', 0))
            print(f"DEBUG: Critères personnalisés triés par ID: {[c.get('id') for c in structure.criteres_personnalises_globaux]}")
        
        # Gestion des modifications de notes maximales pour les critères personnalisés
        for critere in structure.criteres_personnalises_globaux:
            critere_id = critere.get('id')
            note_max_key = f'critere_personnalise_note_max_{critere_id}'
            
            if note_max_key in request.POST:
                try:
                    nouvelle_note_max = int(request.POST.get(note_max_key))
                    if 1 <= nouvelle_note_max <= 20:
                        critere['note_max'] = nouvelle_note_max
                        print(f"DEBUG: Note maximale mise à jour pour le critère {critere.get('nom')}: {nouvelle_note_max}")
                        modifications_effectuees = True
                    else:
                        messages.error(request, f"La note maximale doit être entre 1 et 20 pour le critère '{critere.get('nom')}'.")
                except ValueError:
                    messages.error(request, f"Valeur invalide pour la note maximale du critère '{critere.get('nom')}'.")
        
        # Gestion des compétences des critères fixes
        if not hasattr(structure, 'competences_criteres_fixes') or structure.competences_criteres_fixes is None:
            structure.competences_criteres_fixes = {}
        
        print(f"DEBUG: Compétences critères fixes avant traitement: {structure.competences_criteres_fixes}")
        
        # Initialiser avec les compétences par défaut si vide
        competences_par_defaut = {
            'sciences_geodesiques': [
                'de la géodésie géométrique',
                'de l\'astronomie la géodésie spatiale',
                'de la géodésie physique',
                'Ajustements et compensations par moindres carrées',
                'des systèmes et référentiels géodésiques',
                'des projections cartographiques (carto.mathématique)',
                'de la géodésie appliquée',
                'du GNSS et de',
                'la micro-géodésie y compris les différentes techniques de mesure'
            ],
            'topographie': [
                'Théorique et pratique de la topographie',
                'Topométrique et instrumentation',
                'Techniques de mensuration'
            ],
            'photogrammetrie': [
                'Base et approfondie de la photogrammétrie',
                'Mise en place des photographies aériennes',
                'Aérotriangulation',
                'Restitution photogrammétrique',
                'Génération de produits dérivés (MNT/Ortho)',
                'Drone'
            ],
            'cartographie': [
                'Cartographie topographique',
                'Systèmes de représentation cartographique',
                'Cartographie thématique',
                'Sémiologie et langage cartographique',
                'DAO/CAO',
                'Drone (Cartographie)'
            ],
            'droit_foncier': [
                'Droit foncier',
                'Techniques cadastrales',
                'Gestion foncière et aménagement',
                'Réglementations cadastre et propriété'
            ],
            'sig': [
                'Bases en SIG',
                'Gestion et analyse des données spatiales',
                'Bases de données géographiques',
                'Web mapping'
            ],
            'teledetection': [
                'Bases physiques de la télédétection',
                'Traitement d\'images optique/radar',
                'Applications de la télédétection'
            ]
        }
        
        # Initialiser les compétences par défaut si elles n'existent pas
        for critere_fixe, comps_defaut in competences_par_defaut.items():
            if critere_fixe not in structure.competences_criteres_fixes or not structure.competences_criteres_fixes[critere_fixe]:
                structure.competences_criteres_fixes[critere_fixe] = comps_defaut.copy()
        
        # Liste des critères fixes
        criteres_fixes = ['sciences_geodesiques', 'topographie', 'photogrammetrie', 'cartographie', 'droit_foncier', 'sig', 'teledetection']
        
        for critere_fixe in criteres_fixes:
            # Ajout de compétence pour critère fixe
            ajouter_key = f'ajouter_comp_fixe_{critere_fixe}'
            nouvelle_comp_key = f'nouvelle_comp_fixe_{critere_fixe}'
            
            if ajouter_key in request.POST:
                nouvelle_comp = request.POST.get(nouvelle_comp_key, '').strip()
                print(f"DEBUG: Ajout compétence pour {critere_fixe}: '{nouvelle_comp}'")
                if nouvelle_comp:
                    if critere_fixe not in structure.competences_criteres_fixes:
                        structure.competences_criteres_fixes[critere_fixe] = []
                    structure.competences_criteres_fixes[critere_fixe].append(nouvelle_comp)
                    print(f"DEBUG: Compétence ajoutée. Nouveau contenu: {structure.competences_criteres_fixes[critere_fixe]}")
                    messages.success(request, f"Compétence '{nouvelle_comp}' ajoutée au critère '{critere_fixe}'.")
            
            # Suppression de compétence pour critère fixe
            for idx in range(20):  # Limite arbitraire pour éviter les boucles infinies
                supprimer_key = f'supprimer_comp_fixe_{critere_fixe}_{idx}'
                if supprimer_key in request.POST:
                    print(f"DEBUG: Suppression compétence pour {critere_fixe} à l'index {idx}")
                    print(f"DEBUG: Compétences actuelles: {structure.competences_criteres_fixes.get(critere_fixe, [])}")
                    
                    if critere_fixe in structure.competences_criteres_fixes and idx < len(structure.competences_criteres_fixes[critere_fixe]):
                        comp_supprimee = structure.competences_criteres_fixes[critere_fixe].pop(idx)
                        print(f"DEBUG: Compétence supprimée: '{comp_supprimee}'")
                        print(f"DEBUG: Compétences après suppression: {structure.competences_criteres_fixes[critere_fixe]}")
                        messages.success(request, f"Compétence '{comp_supprimee}' supprimée du critère '{critere_fixe}'.")
                    else:
                        print(f"DEBUG: Impossible de supprimer - critère: {critere_fixe in structure.competences_criteres_fixes}, index: {idx}, longueur: {len(structure.competences_criteres_fixes.get(critere_fixe, []))}")
                    break
        
        # Gestion des stages configurables (seuls les administrateurs peuvent ajouter/supprimer)
        if not hasattr(structure, 'stages_configurables') or structure.stages_configurables is None:
            structure.stages_configurables = []
        
        action_stage = request.POST.get('action_stage')
        if action_stage == 'ajouter':
            nom_stage = request.POST.get('nom_stage_personnalise', '').strip()
            duree_stage = request.POST.get('duree_stage_personnalise', '').strip()
            if nom_stage and duree_stage:
                nouveau_stage = {
                    'id': len(structure.stages_configurables) + 1,
                    'nom': nom_stage,
                    'duree': duree_stage,
                    'actif': True
                }
                structure.stages_configurables.append(nouveau_stage)
                messages.success(request, f"Stage '{nom_stage}' ajouté avec succès.")
        elif action_stage == 'supprimer':
            stage_id = request.POST.get('stage_id')
            if stage_id:
                try:
                    stage_id = int(stage_id)
                    stage_a_supprimer = None
                    for stage in structure.stages_configurables:
                        if stage.get('id') == stage_id:
                            stage_a_supprimer = stage
                            break
                    
                    if stage_a_supprimer:
                        structure.stages_configurables = [
                            s for s in structure.stages_configurables 
                            if s.get('id') != stage_id
                        ]
                        messages.success(request, f"Stage '{stage_a_supprimer.get('nom')}' supprimé avec succès.")
                except ValueError:
                    pass
        
        # Gestion de la suppression des stages par défaut
        stages_par_defaut = [
            'stage_conservation_fonciere',
            'stage_cadastre', 
            'stage_geodesie',
            'stage_topographie',
            'stage_photogrammetrie'
        ]
        
        for stage_defaut in stages_par_defaut:
            if request.POST.get(f'supprimer_stage_defaut_{stage_defaut}'):
                # Marquer le stage comme supprimé dans la structure
                if not hasattr(structure, 'stages_defaut_supprimes') or structure.stages_defaut_supprimes is None:
                    structure.stages_defaut_supprimes = []
                if stage_defaut not in structure.stages_defaut_supprimes:
                    structure.stages_defaut_supprimes.append(stage_defaut)
                messages.success(request, f"Stage par défaut '{stage_defaut}' supprimé avec succès.")
        
        try:
            # Trier les critères personnalisés par ordre d'ajout (par ID) pour garantir l'ordre d'affichage
            if structure.criteres_personnalises_globaux:
                structure.criteres_personnalises_globaux.sort(key=lambda x: x.get('id', 0))
                print(f"DEBUG: Critères personnalisés triés par ID: {[c.get('id') for c in structure.criteres_personnalises_globaux]}")
            
            # Debug: afficher la structure avant sauvegarde
            print(f"DEBUG: Structure avant sauvegarde - Critères personnalisés: {structure.criteres_personnalises_globaux}")
            print(f"DEBUG: Structure avant sauvegarde - Compétences critères fixes: {structure.competences_criteres_fixes}")
            print(f"DEBUG: Structure avant sauvegarde - Stages configurables: {structure.stages_configurables}")
            
            # Forcer la mise à jour des champs JSON
            structure.date_modification = timezone.now()
            
            # Vérifier si c'est une vraie instance de modèle ou une structure temporaire
            if hasattr(structure, '_meta'):  # C'est un vrai modèle Django
                structure.save(force_update=True)
                structure.refresh_from_db()
            else:  # C'est une structure temporaire
                structure.save()
            print(f"DEBUG: Structure après sauvegarde - Critères personnalisés: {structure.criteres_personnalises_globaux}")
            
            messages.success(request, "Structure de la fiche d'évaluation mise à jour avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la sauvegarde : {str(e)}")
            print(f"DEBUG: Erreur de sauvegarde: {str(e)}")
            import traceback
            traceback.print_exc()
        return redirect('dossiers:controle_fiche_evaluation')
    
    # Compétences par défaut pour les critères fixes
    competences_par_defaut = {
        'sciences_geodesiques': [
            'de la géodésie géométrique',
            'de l\'astronomie la géodésie spatiale',
            'de la géodésie physique',
            'Ajustements et compensations par moindres carrées',
            'des systèmes et référentiels géodésiques',
            'des projections cartographiques (carto.mathématique)',
            'de la géodésie appliquée',
            'du GNSS et de',
            'la micro-géodésie y compris les différentes techniques de mesure'
        ],
        'topographie': [
            'Théorique et pratique de la topographie',
            'Topométrique et instrumentation',
            'Techniques de mensuration'
        ],
        'photogrammetrie': [
            'Base et approfondie de la photogrammétrie',
            'Mise en place des photographies aériennes',
            'Aérotriangulation',
            'Restitution photogrammétrique',
            'Génération de produits dérivés (MNT/Ortho)',
            'Drone'
        ],
        'cartographie': [
            'Cartographie topographique',
            'Systèmes de représentation cartographique',
            'Cartographie thématique',
            'Sémiologie et langage cartographique',
            'DAO/CAO',
            'Drone (Cartographie)'
        ],
        'droit_foncier': [
            'Droit foncier',
            'Techniques cadastrales',
            'Gestion foncière et aménagement',
            'Réglementations cadastre et propriété'
        ],
        'sig': [
            'Bases en SIG',
            'Gestion et analyse des données spatiales',
            'Bases de données géographiques',
            'Web mapping'
        ],
        'teledetection': [
            'Bases physiques de la télédétection',
            'Traitement d\'images optique/radar',
            'Applications de la télédétection'
        ]
    }
    
    context = {
        'structure': structure,
        'user': request.user,
        'compétences_sciences_geodesiques': competences_par_defaut['sciences_geodesiques'],
        'compétences_topographie': competences_par_defaut['topographie'],
        'compétences_photogrammetrie': competences_par_defaut['photogrammetrie'],
        'compétences_cartographie': competences_par_defaut['cartographie'],
        'compétences_droit_foncier': competences_par_defaut['droit_foncier'],
        'compétences_sig': competences_par_defaut['sig'],
        'compétences_teledetection': competences_par_defaut['teledetection'],
    }
    return render(request, 'dossiers/controle_fiche_evaluation.html', context)

@login_required
def voir_avis_commission(request, dossier_id):
    """Voir l'avis de commission d'un dossier traité"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    dossier = get_object_or_404(DossierTraite, id=dossier_id)
    
    context = {
        'dossier': dossier,
    }
    return render(request, 'dossiers/voir_avis_commission.html', context)

@login_required
def creer_reunion_multiple(request):
    """Créer une réunion pour plusieurs dossiers traités"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    # Support pour GET (fallback si le modal ne fonctionne pas)
    if request.method == 'GET' and request.GET.get('titre') and request.GET.get('dossiers_ids'):
        titre = request.GET.get('titre')
        dossiers_ids = request.GET.get('dossiers_ids')
        
        # Créer une réunion simple avec les paramètres GET
        try:
            ids_list = [int(id.strip()) for id in dossiers_ids.split(',') if id.strip()]
            dossiers = DossierTraite.objects.filter(id__in=ids_list)
            
            if dossiers.exists():
                from datetime import datetime, timedelta
                date_reunion_obj = datetime.now() + timedelta(days=7)  # Dans une semaine par défaut
                
                participants = f"Admin: {request.user.get_full_name() or request.user.username}"
                ordre_du_jour = f"{titre}\n\nDossiers à traiter:\n"
                
                for dossier in dossiers:
                    ordre_du_jour += f"- {dossier.demandeur_candidat} ({dossier.reference})\n"
                
                decisions = f"Réunion créée le {timezone.now().strftime('%d/%m/%Y à %H:%M')} pour traiter {len(dossiers)} dossier(s)."
                
                reunions_creees = 0
                for dossier in dossiers:
                    try:
                        dossier.ajouter_reunion(
                            date_reunion=date_reunion_obj,
                            participants=participants,
                            ordre_du_jour=ordre_du_jour,
                            decisions=decisions
                        )
                        reunions_creees += 1
                    except Exception as e:
                        print(f"Erreur lors de l'ajout de réunion pour le dossier {dossier.id}: {e}")
                
                messages.success(request, f"Réunion '{titre}' créée avec succès pour {reunions_creees} dossier(s).")
            else:
                messages.error(request, "Aucun dossier valide trouvé.")
                
        except Exception as e:
            messages.error(request, f"Erreur lors de la création : {str(e)}")
        
        return redirect('dossiers:dossiers_traites_admin')
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            titre = request.POST.get('titre')
            date_reunion = request.POST.get('date_reunion')
            description = request.POST.get('description', '')
            dossiers_ids = request.POST.get('dossiers_ids', '')
            
            if not titre or not date_reunion or not dossiers_ids:
                messages.error(request, "Veuillez remplir tous les champs obligatoires.")
                return redirect('dossiers:dossiers_traites_admin')
            
            # Convertir la chaîne d'IDs en liste
            ids_list = [int(id.strip()) for id in dossiers_ids.split(',') if id.strip()]
            
            if not ids_list:
                messages.error(request, "Aucun dossier sélectionné.")
                return redirect('dossiers:dossiers_traites_admin')
            
            # Récupérer les dossiers
            dossiers = DossierTraite.objects.filter(id__in=ids_list)
            
            if not dossiers.exists():
                messages.error(request, "Aucun dossier valide trouvé.")
                return redirect('dossiers:dossiers_traites_admin')
            
            # Convertir date_reunion en datetime
            from datetime import datetime
            date_reunion_obj = datetime.fromisoformat(date_reunion)
            
            # Préparer les informations de la réunion
            participants = f"Admin: {request.user.get_full_name() or request.user.username}"
            ordre_du_jour = f"{titre}\n\nDossiers à traiter:\n"
            
            # Ajouter la liste des dossiers
            for dossier in dossiers:
                ordre_du_jour += f"- {dossier.demandeur_candidat} ({dossier.reference})\n"
            
            if description:
                ordre_du_jour += f"\nDescription: {description}"
            
            decisions = f"Réunion créée le {timezone.now().strftime('%d/%m/%Y à %H:%M')} pour traiter {len(dossiers)} dossier(s)."
            
            # Ajouter la réunion à tous les dossiers sélectionnés
            reunions_creees = 0
            for dossier in dossiers:
                try:
                    dossier.ajouter_reunion(
                        date_reunion=date_reunion_obj,
                        participants=participants,
                        ordre_du_jour=ordre_du_jour,
                        decisions=decisions
                    )
                    reunions_creees += 1
                except Exception as e:
                    print(f"Erreur lors de l'ajout de réunion pour le dossier {dossier.id}: {e}")
            
            if reunions_creees > 0:
                messages.success(request, f"Réunion '{titre}' créée avec succès pour {reunions_creees} dossier(s).")
            else:
                messages.error(request, "Aucune réunion n'a pu être créée.")
            
        except ValueError as e:
            messages.error(request, f"Erreur dans les données : {str(e)}")
        except Exception as e:
            messages.error(request, f"Erreur lors de la création de la réunion : {str(e)}")
    
    return redirect('dossiers:dossiers_traites_admin')

@login_required
def creer_reunion_form(request):
    """Page dédiée pour créer une réunion avec les dossiers sélectionnés"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    # Récupérer les IDs des dossiers sélectionnés
    dossiers_ids = request.GET.get('dossiers_ids', '')
    
    if not dossiers_ids:
        messages.error(request, "Aucun dossier sélectionné.")
        return redirect('dossiers:dossiers_traites_admin')
    
    try:
        ids_list = [int(id.strip()) for id in dossiers_ids.split(',') if id.strip()]
        dossiers = DossierTraite.objects.filter(id__in=ids_list)
        
        if not dossiers.exists():
            messages.error(request, "Aucun dossier valide trouvé.")
            return redirect('dossiers:dossiers_traites_admin')
    
    except ValueError:
        messages.error(request, "IDs de dossiers invalides.")
        return redirect('dossiers:dossiers_traites_admin')
    
    # Traitement du formulaire POST
    if request.method == 'POST':
        try:
            titre = request.POST.get('titre')
            date_reunion = request.POST.get('date_reunion')
            description = request.POST.get('description', '')
            
            # Vérifier que tous les dossiers ont une décision
            decisions_manquantes = []
            for dossier in dossiers:
                decision_key = f'decision_{dossier.id}'
                decision_value = request.POST.get(decision_key, '').strip()
                if not decision_value:
                    decisions_manquantes.append(f"{dossier.demandeur_candidat} ({dossier.numero})")
            
            if not titre or not date_reunion:
                messages.error(request, "Veuillez remplir tous les champs obligatoires.")
                return render(request, 'dossiers/creer_reunion_form.html', {
                    'dossiers': dossiers,
                    'dossiers_count': len(dossiers),
                    'dossiers_ids': dossiers_ids
                })
            
            if decisions_manquantes:
                messages.error(request, f"Veuillez remplir les décisions pour : {', '.join(decisions_manquantes)}")
                return render(request, 'dossiers/creer_reunion_form.html', {
                    'dossiers': dossiers,
                    'dossiers_count': len(dossiers),
                    'dossiers_ids': dossiers_ids
                })
            
            # Convertir date_reunion en datetime
            from datetime import datetime
            date_reunion_obj = datetime.fromisoformat(date_reunion)
            
            # Préparer les informations de la réunion
            participants = f"Admin: {request.user.get_full_name() or request.user.username}"
            ordre_du_jour = f"{titre}\n\nDossiers à traiter:\n"
            
            # Ajouter la liste des dossiers
            for dossier in dossiers:
                ordre_du_jour += f"- {dossier.demandeur_candidat} ({dossier.reference})\n"
            
            if description:
                ordre_du_jour += f"\nDescription générale: {description}"
            
            # Ajouter la réunion avec décision individuelle pour chaque dossier
            reunions_creees = 0
            for dossier in dossiers:
                try:
                    # Récupérer la décision spécifique pour ce dossier
                    decision_key = f'decision_{dossier.id}'
                    decision_individuelle = request.POST.get(decision_key, '').strip()
                    
                    # Créer les décisions spécifiques pour ce dossier
                    decisions_dossier = f"Réunion '{titre}' du {date_reunion_obj.strftime('%d/%m/%Y à %H:%M')}\n\n"
                    decisions_dossier += f"Décision pour {dossier.demandeur_candidat} ({dossier.numero}):\n"
                    decisions_dossier += f"{decision_individuelle}\n\n"
                    decisions_dossier += f"Validé par: {request.user.get_full_name() or request.user.username}"
                    
                    dossier.ajouter_reunion(
                        date_reunion=date_reunion_obj,
                        participants=participants,
                        ordre_du_jour=ordre_du_jour,
                        decisions=decisions_dossier
                    )
                    reunions_creees += 1
                except Exception as e:
                    print(f"Erreur lors de l'ajout de réunion pour le dossier {dossier.id}: {e}")
            
            if reunions_creees > 0:
                messages.success(request, f"Réunion '{titre}' créée avec succès pour {reunions_creees} dossier(s) avec décisions individuelles.")
                return redirect('dossiers:dossiers_traites_admin')
            else:
                messages.error(request, "Aucune réunion n'a pu être créée.")
            
        except ValueError as e:
            messages.error(request, f"Erreur dans la date : {str(e)}")
        except Exception as e:
            messages.error(request, f"Erreur lors de la création de la réunion : {str(e)}")
    
    # Affichage du formulaire (GET)
    context = {
        'dossiers': dossiers,
        'dossiers_count': len(dossiers),
        'dossiers_ids': dossiers_ids
    }
    return render(request, 'dossiers/creer_reunion_form.html', context)

@login_required
def supprimer_dossier_traite(request, dossier_id):
    """Vue pour supprimer un dossier traité"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    try:
        # Vérifier si le dossier traité existe (modèle DossierTraite)
        dossier = DossierTraite.objects.get(id=dossier_id)
        print(f"✅ Dossier traité trouvé: ID {dossier_id}, Numéro: {dossier.numero}")
        
    except DossierTraite.DoesNotExist:
        print(f"❌ Dossier traité non trouvé: ID {dossier_id}")
        messages.error(request, f"Dossier traité avec l'ID {dossier_id} non trouvé. Il a peut-être été supprimé entre-temps.")
        return redirect('dossiers:dossiers_traites_admin')
    
    if request.method == 'POST':
        try:
            # Supprimer le dossier traité
            numero_dossier = dossier.numero
            candidat_dossier = dossier.demandeur_candidat
            dossier.delete()
            
            messages.success(request, f"Dossier traité '{numero_dossier}' ({candidat_dossier}) supprimé avec succès")
            return redirect('dossiers:dossiers_traites_admin')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression : {str(e)}")
            return redirect('dossiers:dossiers_traites_admin')
    
    context = {
        'dossier': dossier,
    }
    return render(request, 'dossiers/confirmer_suppression_dossier_traite.html', context)
