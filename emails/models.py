from django.db import models

# Create your models here.
class RecipientCategory(models.TextChoices):
    MSP = "MSP", "MSP"
    FDP = "FDP", "FDP"
    RP = "RP", "RP"
    REPORT = "REPORT", "Report"


class RecipientGroup(models.Model):
    """Represents one key from your old dicts, e.g. category=MSP, name='Egypro'."""
    category = models.CharField(max_length=20, choices=RecipientCategory.choices)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("category", "name")

    def __str__(self):
        return f"{self.get_category_display()} — {self.name}"


class RecipientEmail(models.Model):
    """One email address belonging to a group. This is what the client edits."""
    group = models.ForeignKey(RecipientGroup, related_name="emails", on_delete=models.CASCADE)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("group", "email")

    def __str__(self):
        return self.email

class MSPEscalationChoices(models.TextChoices):
    EGYPRO = "Egypro", "Egypro"
    CAMUSAT = "Camusat", "Camusat"
    ADRIAN = "Adrian", "Adrian"
    KINDE = "Kinde", "Kinde"
    FIRESIDE = "Fireside", "Fireside"
    SOLITON = "Soliton", "Soliton"
    SOVEREIGN = "Sovereign", "Sovereign"
    OPTIMAX = "Optimax", "Optimax"
    TETRANET = "Tetranet", "Tetranet"
    COREVANTAGE = "Corevantage", "Corevantage"


class MSPEscalationRole(models.TextChoices):
    PROJECT_MANAGER = "Project Manager", "Project Manager"
    TECHNICAL_PROJECT_MANAGER = (
        "Technical Project Manager",
        "Technical Project Manager"
    )
    CHIEF_OPERATING_OFFICER = (
        "Chief Operating Officer",
        "Chief Operating Officer"
    )
    CHIEF_TECHNICAL_OFFICER = (
        "Chief Technical Officer",
        "Chief Technical Officer"
    )
    CHIEF_EXECUTIVE_OFFICER = (
        "Chief Executive Officer",
        "Chief Executive Officer"
    )

class MSPEscalationMatrix(models.Model):
    msp = models.CharField(
        max_length=50,
        choices=MSPEscalationChoices.choices,
        unique=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_msp_display()

class MSPEscalationEmail(models.Model):
    matrix = models.ForeignKey(
        MSPEscalationMatrix,
        on_delete=models.CASCADE,
        related_name="emails"
    )
    role = models.CharField(
        max_length=50,
        choices=MSPEscalationRole.choices
    )
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("matrix", "role", "email")

    def __str__(self):
        return f"{self.matrix.msp} — {self.get_role_display()} — {self.email}"

class HODEscalationEmail(models.Model):
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("email",)

    def __str__(self):
        return self.email
