from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import StudentProfile

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    This function ensures that a StudentProfile is created or updated every time
    a User is saved.
    """
    if created:
        # Create a StudentProfile when a new user is created
        StudentProfile.objects.create(user=instance)
    else:
        # If the user already exists, check for the related profile
        if hasattr(instance, 'studentprofile'):
            # If the user already has a profile, just save it
            instance.studentprofile.save()
        else:
            # If the user doesn't have a profile, create one
            StudentProfile.objects.create(user=instance)
