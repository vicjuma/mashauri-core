from django.db import models
from django.contrib.auth.models import AbstractBaseUser, \
    UserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta


class CustomUserManager(UserManager):
    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("You must provide a username")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MSP = "MSP", "MSP"
        FDP = "FDP", "FDP"
        ENTERPRISE_CONNECTIVITY = (
            "ENTERPRISE CONNECTIVITY", "ENTERPRISE CONNECTIVITY")
        ENTERPRISE_PROJECT = "ENTERPRISE_PROJECT", "ENTERPRISE_PROJECT"
        SUPPORT = "SUPPORT", "SUPPORT"
        ROLLOUT_PARTNER = "ROLLOUT_PARTNER", "ROLLOUT_PARTNER"

    class MSP(models.TextChoices):
        No_msp = "None", "None"
        Egypro = "Egypro", "Egypro"
        Camusat = "Camusat", "Camusat"
        Adrian = "Adrian", "Adrian"
        Kinde = "Kinde", "Kinde"
        Fireside = "Fireside", "Fireside"
        Soliton = "Soliton", "Soliton"

    class FDP(models.TextChoices):
        No_fdp = "None", "None"
        Fireside = "Fireside", "Fireside"
        Broadcom = "Broadcom", "Broadcom"
        Optimax = "Optimax", "Optimax"
        BTN = "BTN", "BTN"
        Com21 = "Com21", "Com21"
        Bens = "Bens", "Bens"
        Geonet = "Geonet", "Geonet"

    class RP(models.TextChoices):
        No_rp = "None", "None"
        Fireside = "Fireside", "Fireside"
        Kinde = "Kinde", "Kinde"
        Hatikvah = "Hatikvah", "Hatikvah"
        Camusat = "Camusat", "Camusat"
        Techminds = "Techminds", "Techminds"
        Egypro = "Egypro", "Egypro"
        Optimax = "Optimax", "Optimax"
        Pavicon = "Pavicon", "Pavicon"
        Decko = "Decko", "Decko"
        Adrian = "Adrian", "Adrian"
        Powergen = "Powergen", "Powergen"
        Tetranet = "Tetranet", "Tetranet"
        Extra_Dimensions = "Extra Dimensions", "Extra Dimensions"
        Quavatel = "Quavatel", "Quavatel"
        Acl = "Acl", "Acl"

    base_role = Role.ADMIN
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, blank=True, default="")
    first_name = models.CharField(max_length=50, blank=True, default="")
    last_name = models.CharField(max_length=50, blank=True, default="")
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    role = models.CharField(max_length=50, choices=Role.choices)
    msp_category = models.CharField(
        max_length=50, choices=MSP.choices,
        default=MSP.No_msp, blank=False, null=True)
    fdp_category = models.CharField(
        max_length=50, choices=FDP.choices,
        default=FDP.No_fdp, blank=False, null=True)
    rp_category = models.CharField(
        max_length=50, choices=RP.choices,
        default=RP.No_rp, blank=False, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'mashauri_users'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.email.split('@')[0]


class Dispatch(models.Model):
    ESCALATION_CHOICES = [
        ('Proactive', 'Proactive'),
        ('Reactive', 'Reactive'),
        ('Interception', 'Interception'),
        ('Support', 'Support'),
        ('Optimization', 'Optimization'),
    ]

    MSP_CHOICES = [
        ('None', 'None'),
        ('Egypro', 'Egypro'),
        ('Camusat', 'Camusat'),
        ('Adrian', 'Adrian'),
        ('Kinde', 'Kinde'),
        ('Fireside', 'Fireside'),
        ('Soliton', 'Soliton'),
    ]

    FDP_CHOICES = [
        ('Fireside', 'Fireside'),
        ('Broadcom', 'Broadcom'),
        ('Optimax', 'Optimax'),
        ('BTN', 'BTN'),
        ('Com21', 'Com21'),
        ('Bens', 'Bens'),
        ('Geonet', 'Geonet'),
    ]

    STATUS_CHOICES = [
        ('Hold', 'Hold'),
        ('Progress', 'Progress'),
        ('Closed', 'Closed'),
    ]

    EC_CHOICES = [
        ('Steven Ogola', 'Steven Ogola'),
        ('Emmanuel Muteti', 'Emmanuel Muteti'),
        ('Paul Msava', 'Paul Msava'),
        ('Kevin Waswa', 'Kevin Waswa'),
    ]

    RP_CHOICES = [
        ('None', 'None'),
        ('Fireside', 'Fireside'),
        ('Kinde', 'Kinde'),
        ('Hatikvah', 'Hatikvah'),
        ('Camusat', 'Camusat'),
        ('Techminds', 'Techminds'),
        ('Egypro', 'Egypro'),
        ('Optimax', 'Optimax'),
        ('Pavicon', 'Pavicon'),
        ('Decko', 'Decko'),
        ('Adrian', 'Adrian'),
        ('Powergen', 'Powergen'),
        ('Tetranet', 'Tetranet'),
        ('Extra Dimensions', 'Extra Dimensions'),
        ('Quavatel', 'Quavatel'),
        ('Acl', 'Acl'),
    ]

    building_name = models.CharField(max_length=50)
    building_id = models.CharField(max_length=50, null=True, blank=True)
    msp = models.CharField(
        max_length=50,
        choices=MSP_CHOICES, default=None, null=True)
    fdp = models.CharField(max_length=50, choices=FDP_CHOICES)
    rp = models.CharField(max_length=50, choices=RP_CHOICES)
    ec = models.CharField(
        max_length=50,
        choices=EC_CHOICES, default='Steven Ogola')
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES, default='Progress')
    escalation_type = models.CharField(
        max_length=50,
        choices=ESCALATION_CHOICES)
    comments = models.TextField(null=True, blank=True)
    coordinates = models.CharField(
        max_length=50, null=True, blank=True,
        help_text='Latitude and Longitude tuple as "latitude,longitude"')
    client_id = models.CharField(max_length=50, null=True, blank=True)
    client_name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_expired = models.BooleanField(default=False, db_index=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    sla_timer = models.DateTimeField(null=True, blank=True)
    ticketing = models.OneToOneField(
        'Ticket', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dispatch')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True)
    reassign_to = models.CharField(
        max_length=50, null=True,
        default=None, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.id} - {self.building_name}'

    def save(self, *args, **kwargs):
        if not self.id:
            if self.escalation_type == 'Proactive':
                self.sla_timer = timezone.now() + timedelta(hours=120)
            elif (
                    (self.escalation_type == 'Reactive') or (
                            self.escalation_type == 'Interception')):
                self.sla_timer = timezone.now() + timedelta(hours=36)
            elif self.escalation_type == 'Support':
                self.sla_timer = timezone.now() + timedelta(hours=22)
            else:
                self.sla_timer = timezone.now() + timedelta(hours=24)
        super(Dispatch, self).save(*args, **kwargs)

    class Meta:
        db_table = 'mashauri_dispatches'
        verbose_name_plural = 'Dispatches'


class DispatchImage(models.Model):
    dispatch = models.ForeignKey(
        Dispatch, on_delete=models.CASCADE,
        related_name='images')
    image = models.ImageField(upload_to='dispatch_images/')
    image_type = models.CharField(max_length=50, default='creation')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for Dispatch {self.dispatch.id} - {self.image_type}'

    class Meta:
        db_table = 'mashauri_dispatch_images'
        verbose_name = 'Dispatch Image'
        verbose_name_plural = 'Dispatch Images'


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Closed', 'Closed'),
    ]
    dispatching = models.OneToOneField(Dispatch, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        User, on_delete=models.CASCADE,
        null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'Ticket for Dispatch ID: {self.dispatch.id}'

    class Meta:
        db_table = 'mashauri_tickets'


class SLA(models.Model):
    dispatch = models.ForeignKey(Dispatch, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f'SLA for Dispatch ID: {self.dispatch.id}'

    class Meta:
        db_table = 'mashauri_SLAs'
        verbose_name = 'SLA'
        verbose_name_plural = 'SLAs'


class Comment(models.Model):
    dispatch = models.ForeignKey(Dispatch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.created_at}'

    class Meta:
        db_table = 'mashauri_dispatch_comments'
        verbose_name = 'Dispatch Comment'
        verbose_name_plural = 'Dispatch Comments'
