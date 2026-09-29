from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import RecipientGroup, RecipientEmail, MSPEscalationEmail, MSPEscalationMatrix, HODEscalationEmail


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

@admin.register(HODEscalationEmail)
class HODEscalationEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("email",)
