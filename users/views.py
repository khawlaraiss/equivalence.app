from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, label='Rôle')
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe déjà.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

def login_view(request):
    """Vue de connexion personnalisée"""
    if request.user.is_authenticated:
        return redirect('dossiers:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue, {user.username}!")
            return redirect('dossiers:dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'users/login.html')

@login_required
def create_user(request):
    """Vue pour créer un nouvel utilisateur (admin seulement)"""
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent créer des utilisateurs")
        return redirect('dossiers:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Vérifier si l'utilisateur existe déjà
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                
                if CustomUser.objects.filter(username=username).exists():
                    messages.error(request, f"Le nom d'utilisateur '{username}' existe déjà.")
                    return render(request, 'users/create_user.html', {'form': form})
                
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(request, f"L'email '{email}' est déjà utilisé.")
                    return render(request, 'users/create_user.html', {'form': form})
                
                # Créer l'utilisateur
                user = form.save()
                messages.success(request, f'Utilisateur "{user.username}" créé avec succès')
                return redirect('users:gestion_utilisateurs')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création de l'utilisateur : {str(e)}")
                return render(request, 'users/create_user.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/create_user.html', {'form': form})

def logout_view(request):
    """Vue de déconnexion personnalisée"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('/login/')

@login_required
def profile(request):
    """Vue du profil utilisateur"""
    # Calcul des statistiques pour les professeurs
    if request.user.role == 'professeur':
        total_dossiers = request.user.dossiers_attribues.count()
        dossiers_traites = request.user.dossiers_attribues.filter(statut='traite').count()
        dossiers_en_cours = request.user.dossiers_attribues.filter(statut='en_cours').count()
        dossiers_non_traites = request.user.dossiers_attribues.filter(statut='non_traite').count()
    else:
        # Pour les administrateurs, on peut afficher des statistiques globales
        from dossiers.models import Dossier
        total_dossiers = Dossier.objects.count()
        dossiers_traites = Dossier.objects.filter(statut='traite').count()
        dossiers_en_cours = Dossier.objects.filter(statut='en_cours').count()
        dossiers_non_traites = Dossier.objects.filter(statut='non_traite').count()
    
    context = {
        'user': request.user,
        'total_dossiers': total_dossiers,
        'dossiers_traites': dossiers_traites,
        'dossiers_en_cours': dossiers_en_cours,
        'dossiers_non_traites': dossiers_non_traites,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def gestion_utilisateurs(request):
    """Interface de gestion des utilisateurs"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    utilisateurs = CustomUser.objects.all().order_by('username')
    
    # Filtrage par rôle
    role_filter = request.GET.get('role')
    if role_filter:
        utilisateurs = utilisateurs.filter(role=role_filter)
    
    # Calcul des statistiques
    total_utilisateurs = CustomUser.objects.count()
    administrateurs = CustomUser.objects.filter(role='admin').count()
    professeurs = CustomUser.objects.filter(role='professeur').count()
    
    context = {
        'utilisateurs': utilisateurs,
        'total_utilisateurs': total_utilisateurs,
        'administrateurs': administrateurs,
        'professeurs': professeurs,
    }
    return render(request, 'users/gestion_utilisateurs.html', context)

@login_required
def ajouter_utilisateur(request):
    """Ajouter un nouvel utilisateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')
        
        try:
            utilisateur = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                password=password
            )
            messages.success(request, f"Utilisateur {username} créé avec succès")
        except Exception as e:
            messages.error(request, f"Erreur lors de la création : {str(e)}")
        
        return redirect('users:gestion_utilisateurs')
    
    return redirect('users:gestion_utilisateurs')

@login_required
def modifier_utilisateur(request, user_id):
    """Modifier un utilisateur existant"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    utilisateur = CustomUser.objects.get(id=user_id)
    
    if request.method == 'POST':
        try:
            # Mettre à jour les informations de base
            utilisateur.username = request.POST.get('username')
            utilisateur.first_name = request.POST.get('first_name')
            utilisateur.last_name = request.POST.get('last_name')
            utilisateur.email = request.POST.get('email')
            utilisateur.role = request.POST.get('role')
            
            # Mettre à jour le mot de passe si fourni
            password = request.POST.get('password')
            if password:
                utilisateur.set_password(password)
            
            utilisateur.save()
            messages.success(request, f"Utilisateur {utilisateur.username} modifié avec succès")
            return redirect('users:gestion_utilisateurs')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification : {str(e)}")
    
    context = {
        'utilisateur': utilisateur,
        'roles': CustomUser.ROLE_CHOICES,
    }
    return render(request, 'users/modifier_utilisateur.html', context)

@login_required
def desactiver_utilisateur(request, user_id):
    """Désactiver/Activer un utilisateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('dossiers:dashboard')
    
    if request.method == 'POST':
        try:
            utilisateur = CustomUser.objects.get(id=user_id)
            
            # Empêcher l'auto-désactivation
            if utilisateur == request.user:
                messages.error(request, "Vous ne pouvez pas désactiver votre propre compte")
                return redirect('users:gestion_utilisateurs')
            
            # Basculer le statut
            utilisateur.is_active = not utilisateur.is_active
            utilisateur.save()
            
            status = "activé" if utilisateur.is_active else "désactivé"
            messages.success(request, f"Utilisateur {utilisateur.username} {status} avec succès")
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification du statut : {str(e)}")
    
    return redirect('users:gestion_utilisateurs')

def inscription(request):
    """Inscription publique d'un nouvel utilisateur"""
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation des données
        if not all([username, first_name, last_name, email, password, password_confirm]):
            messages.error(request, "Tous les champs sont obligatoires")
            return render(request, 'users/inscription.html')
        
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return render(request, 'users/inscription.html')
        
        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères")
            return render(request, 'users/inscription.html')
        
        try:
            # Vérifier si l'username existe déjà
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur existe déjà")
                return render(request, 'users/inscription.html')
            
            # Vérifier si l'email existe déjà
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Cet email est déjà utilisé")
                return render(request, 'users/inscription.html')
            
            # Créer l'utilisateur (par défaut professeur et actif)
            utilisateur = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                role='professeur',  # Par défaut professeur
                is_active=True      # Actif par défaut
            )
            
            messages.success(request, f"Compte créé avec succès ! Vous pouvez maintenant vous connecter avec {username}")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du compte : {str(e)}")
    
    return render(request, 'users/inscription.html')

@login_required
def supprimer_utilisateur(request, user_id):
    """Supprimer définitivement un utilisateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('users:gestion_utilisateurs')
    
    if request.method == 'POST':
        try:
            utilisateur = CustomUser.objects.get(id=user_id)
            
            # Empêcher l'auto-suppression
            if utilisateur == request.user:
                messages.error(request, "Vous ne pouvez pas supprimer votre propre compte")
                return redirect('users:gestion_utilisateurs')
            
            # Empêcher la suppression du dernier admin
            if utilisateur.role == 'admin':
                admins_count = CustomUser.objects.filter(role='admin').count()
                if admins_count <= 1:
                    messages.error(request, "Impossible de supprimer le dernier administrateur")
                    return redirect('users:gestion_utilisateurs')
            
            # Sauvegarder le nom pour le message
            username = utilisateur.username
            
            # Supprimer l'utilisateur
            utilisateur.delete()
            
            messages.success(request, f"Utilisateur '{username}' supprimé définitivement avec succès")
            
        except CustomUser.DoesNotExist:
            messages.error(request, "Utilisateur non trouvé")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    
    return redirect('users:gestion_utilisateurs')
