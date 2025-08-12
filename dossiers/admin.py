from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django import forms
from .models import Dossier, EtatDossier, RapportAnalyse, ConsistanceAcademique, DossierTraite, Candidat, StructureEvaluationGlobale

@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ['titre', 'statut', 'date_reception']
    list_filter = ['statut', 'date_reception']
    search_fields = ['titre', 'description']
    readonly_fields = ['date_reception']

@admin.register(RapportAnalyse)
class RapportAnalyseAdmin(admin.ModelAdmin):
    list_display = ['dossier', 'titre', 'type_rapport', 'date_rapport']
    list_filter = ['date_rapport', 'type_rapport']
    search_fields = ['dossier__titre', 'titre']

@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
    list_display = ['nom', 'pays_origine', 'date_arrivee', 'dossier']
    list_filter = ['pays_origine', 'date_arrivee']
    search_fields = ['nom', 'pays_origine']

@admin.register(EtatDossier)
class EtatDossierAdmin(admin.ModelAdmin):
    list_display = ['candidat', 'est_nouveau_dossier', 'date_modification']
    list_filter = ['est_nouveau_dossier', 'date_modification']
    search_fields = ['candidat__nom']

@admin.register(ConsistanceAcademique)
class ConsistanceAcademiqueAdmin(admin.ModelAdmin):
    list_display = ['candidat', 'note_totale', 'date_creation']
    list_filter = ['date_creation']
    search_fields = ['candidat__nom']
    readonly_fields = ['note_totale']

class DossierTraiteAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'demandeur_candidat', 'reference', 'date_reception', 
        'diplome', 'universite', 'pays', 'date_avis', 'avis_commission',
        'nombre_reunions', 'actions_buttons'
    ]
    list_filter = [
        'universite', 'pays', 'date_reception', 'date_avis',
        ('avis_commission', admin.EmptyFieldListFilter),
    ]
    search_fields = [
        'numero', 'demandeur_candidat', 'reference', 'diplome', 
        'universite', 'pays', 'avis_commission'
    ]
    readonly_fields = ['nombre_reunions', 'derniere_reunion']
    ordering = ['-date_reception']
    list_per_page = 50
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('numero', 'demandeur_candidat', 'reference')
        }),
        ('Dates et réception', {
            'fields': ('date_envoi', 'reference_reception', 'date_reception')
        }),
        ('Informations académiques', {
            'fields': ('diplome', 'universite', 'universite_autre', 'pays', 'pays_autre')
        }),
        ('Décision de la commission', {
            'fields': ('date_avis', 'avis_commission')
        }),
        ('Réunions', {
            'fields': ('reunions', 'nombre_reunions', 'derniere_reunion'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_reunions(self, obj):
        return obj.get_nombre_reunions()
    nombre_reunions.short_description = 'Nombre de réunions'
    
    def derniere_reunion(self, obj):
        derniere = obj.get_derniere_reunion()
        if derniere:
            return f"{derniere['date']} - {derniere['participants']}"
        return "Aucune réunion"
    derniere_reunion.short_description = 'Dernière réunion'
    
    def actions_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}">Modifier</a> '
            '<a class="button" href="{}">Réunions</a> '
            '<a class="button" href="{}">Avis</a>',
            reverse('admin:dossiers_dossiertraite_change', args=[obj.pk]),
            reverse('dossiers:voir_reunions_dossier', args=[obj.pk]),
            reverse('dossiers:voir_avis_commission', args=[obj.pk])
        )
    actions_buttons.short_description = 'Actions'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='dossiers_dossiertraite_import_excel'),
            path('export-excel/', self.admin_site.admin_view(self.export_excel_view), name='dossiers_dossiertraite_export_excel'),
            path('bulk-edit/', self.admin_site.admin_view(self.bulk_edit_view), name='dossiers_dossiertraite_bulk_edit'),
            path('statistics/', self.admin_site.admin_view(self.statistics_view), name='dossiers_dossiertraite_statistics'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_export'] = True
        return super().changelist_view(request, extra_context)
    
    def import_excel_view(self, request):
        if request.method == 'POST':
            try:
                from .views import import_excel_dossiers
                return import_excel_dossiers(request)
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'import: {e}')
        
        context = {
            'title': 'Importer des dossiers depuis Excel',
            'opts': self.model._meta,
        }
        return render(request, 'admin/dossiers/dossiertraite/import_excel.html', context)
    
    def export_excel_view(self, request):
        import pandas as pd
        from django.http import HttpResponse
        from datetime import datetime
        
        # Récupérer tous les dossiers traités
        dossiers = DossierTraite.objects.all()
        
        # Créer un DataFrame
        data = []
        for dossier in dossiers:
            data.append({
                'Numéro': dossier.numero,
                'Demandeur': dossier.demandeur,
                'Référence': dossier.reference,
                'Date envoi': dossier.date_envoi,
                'Référence réception': dossier.reference_reception,
                'Date réception': dossier.date_reception,
                'Diplôme': dossier.diplome,
                'Université': dossier.universite,
                'Pays': dossier.pays,
                'Date avis': dossier.date_avis,
                'Avis commission': dossier.avis_commission,
                'Nombre réunions': dossier.get_nombre_reunions(),
            })
        
        df = pd.DataFrame(data)
        
        # Créer la réponse HTTP
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="dossiers_traites_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        df.to_excel(response, index=False)
        return response
    
    def bulk_edit_view(self, request):
        if request.method == 'POST':
            selected_ids = request.POST.getlist('_selected_action')
            action = request.POST.get('action')
            
            if action == 'update_universite':
                nouvelle_universite = request.POST.get('nouvelle_universite')
                DossierTraite.objects.filter(id__in=selected_ids).update(universite=nouvelle_universite)
                messages.success(request, f'{len(selected_ids)} dossiers mis à jour')
            
            elif action == 'update_pays':
                nouveau_pays = request.POST.get('nouveau_pays')
                DossierTraite.objects.filter(id__in=selected_ids).update(pays=nouveau_pays)
                messages.success(request, f'{len(selected_ids)} dossiers mis à jour')
            
            elif action == 'update_avis':
                nouvel_avis = request.POST.get('nouvel_avis')
                DossierTraite.objects.filter(id__in=selected_ids).update(avis_commission=nouvel_avis)
                messages.success(request, f'{len(selected_ids)} dossiers mis à jour')
            
            elif action == 'delete_selected':
                DossierTraite.objects.filter(id__in=selected_ids).delete()
                messages.success(request, f'{len(selected_ids)} dossiers supprimés')
            
            return HttpResponseRedirect(reverse('admin:dossiers_dossiertraite_changelist'))
        
        context = {
            'title': 'Modification en masse des dossiers',
            'opts': self.model._meta,
            'dossiers': DossierTraite.objects.all(),
        }
        return render(request, 'admin/dossiers/dossiertraite/bulk_edit.html', context)
    
    def statistics_view(self, request):
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Statistiques générales
        total_dossiers = DossierTraite.objects.count()
        dossiers_avec_avis = DossierTraite.objects.filter(avis_commission__isnull=False).exclude(avis_commission='').count()
        dossiers_sans_avis = total_dossiers - dossiers_avec_avis
        
        # Statistiques par université
        universites_stats = DossierTraite.objects.values('universite').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Statistiques par pays
        pays_stats = DossierTraite.objects.values('pays').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Statistiques par mois (12 derniers mois)
        stats_mensuelles = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            mois = date.strftime('%Y-%m')
            count = DossierTraite.objects.filter(
                date_reception__startswith=mois
            ).count()
            stats_mensuelles.append({'mois': mois, 'count': count})
        
        context = {
            'title': 'Statistiques des dossiers traités',
            'opts': self.model._meta,
            'total_dossiers': total_dossiers,
            'dossiers_avec_avis': dossiers_avec_avis,
            'dossiers_sans_avis': dossiers_sans_avis,
            'universites_stats': universites_stats,
            'pays_stats': pays_stats,
            'stats_mensuelles': stats_mensuelles,
        }
        return render(request, 'admin/dossiers/dossiertraite/statistics.html', context)

# Formulaire personnalisé pour l'édition en masse
class BulkEditForm(forms.Form):
    ACTION_CHOICES = [
        ('update_universite', 'Mettre à jour l\'université'),
        ('update_pays', 'Mettre à jour le pays'),
        ('update_avis', 'Mettre à jour l\'avis'),
        ('delete_selected', 'Supprimer les dossiers sélectionnés'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES, label='Action')
    nouvelle_universite = forms.CharField(required=False, label='Nouvelle université')
    nouveau_pays = forms.CharField(required=False, label='Nouveau pays')
    nouvel_avis = forms.CharField(required=False, label='Nouvel avis', widget=forms.Textarea)

# Enregistrement des modèles dans l'admin
admin.site.register(DossierTraite, DossierTraiteAdmin)
# Les autres modèles sont déjà enregistrés avec @admin.register
