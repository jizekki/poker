import random
import string
from django.db import models
from django.utils.text import slugify


class PokerSession(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    public_identifier = models.CharField(max_length=6)
    is_estimation_running = models.BooleanField(default=False)
    running_index = models.PositiveIntegerField(default=0)

    @staticmethod
    def generate_public_identifier():
        while True:
            identifier = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            existing_objects = PokerSession.objects.filter(public_identifier=identifier)
            if existing_objects.count() == 0:
                return identifier

    def start_estimation(self):
        self.is_estimation_running = True
        self.running_index += 1
        self.save()

    def stop_estimation(self):
        self.is_estimation_running = False
        self.save()


class UserRole(models.TextChoices):
        ORGANIZER = 0, "Organizer"
        PARTICIPANT = 1, "Participant"

class UserStatus(models.TextChoices):
    PENDING = 0, "PENDING"
    ESTIMATION_RUNNING = 1, "ESTIMATION_RUNNING"
    ESTIMATION_SUBMITTED = 2, "ESTIMATION_SUBMITTED"


class User(models.Model):
    slug = models.SlugField(unique=True)
    username = models.CharField(max_length=8)
    session_id = models.ForeignKey(to="poker.PokerSession", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.PARTICIPANT)
    status = models.CharField(max_length=10, choices=UserStatus.choices, default=UserStatus.PENDING)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username + self.session_id.public_identifier)
        super(User, self).save(*args, **kwargs)

class PossibleEstimation(models.Model):
    value = models.FloatField()
    display_name = models.CharField(max_length=10)

class Estimation(models.Model):
    possible_estimation_id = models.ForeignKey(to="poker.PossibleEstimation", on_delete=models.CASCADE)
    user_id = models.ForeignKey(to="poker.User", on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
