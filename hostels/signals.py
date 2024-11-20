from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import StudentProfile

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    # Only create a StudentProfile if it doesn't already exist
    if created:
        StudentProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'studentprofile'):
            instance.studentprofile.save()
        else:
            StudentProfile.objects.create(user=instance)
