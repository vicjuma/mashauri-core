from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import RecipientGroup, RecipientEmail, MSPEscalationEmail, MSPEscalationMatrix, SafaricomEscalationEmail


class RecipientEmailInline(admin.TabularInline):
    model = RecipientEmail
    extra = 1

class MSPEscalationEmailInline(admin.TabularInline):
    model = MSPEscalationEmail
    extra = 1


@admin.register(MSPEscalationMatrix)
class MSPEscalationMatrixAdmin(admin.ModelAdmin):
    list_display = ("msp", "is_active")
    list_filter = ("msp", "is_active")
    search_fields = ("msp",)
    inlines = [MSPEscalationEmailInline]


@admin.register(RecipientGroup)
class RecipientGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    inlines = [RecipientEmailInline]

@admin.register(SafaricomEscalationEmail)
class SafaricomEscalationEmailAdmin(admin.ModelAdmin):
    list_display = ("role", "escalation_days", "email", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("email",)
    list_editable = ("escalation_days", "is_active")
