from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Rôle', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rôle', {'fields': ('role',)}),
    )
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} utilisateur(s) activé(s) avec succès.')
    activate_users.short_description = "Activer les utilisateurs sélectionnés"
    
    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} utilisateur(s) désactivé(s) avec succès.')
    deactivate_users.short_description = "Désactiver les utilisateurs sélectionnés"
    
    def make_staff(self, request, queryset):
        count = queryset.update(is_staff=True)
        self.message_user(request, f'{count} utilisateur(s) promu(s) au statut de staff avec succès.')
    make_staff.short_description = "Promouvoir au statut de staff"
    
    def remove_staff(self, request, queryset):
        count = queryset.update(is_staff=False)
        self.message_user(request, f'{count} utilisateur(s) retiré(s) du statut de staff avec succès.')
    remove_staff.short_description = "Retirer le statut de staff"
    
    actions = [activate_users, deactivate_users, make_staff, remove_staff]
