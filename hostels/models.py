import random
import string
from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.utils.html import format_html
from django.template.loader import render_to_string
from django.urls import reverse


class Amenity(models.Model):
    name = models.CharField(max_length=100)  # e.g., 'Electricity', 'Wi-Fi', etc.

    def __str__(self):
        return self.name


# Hostel model
class Hostel(models.Model):
    name = models.CharField(max_length=40)
    location = models.CharField(max_length=20)
    main_image = models.ImageField(upload_to='media/main') 
    total_rooms = models.DecimalField(max_digits=4, decimal_places=2)
    amenities = models.ManyToManyField(Amenity, related_name='hostels')

    def __str__(self):
        return self.name


class RoomType(models.Model):
    hostel = models.ForeignKey(Hostel, related_name='room_types', on_delete=models.CASCADE)
    room_name = models.CharField(max_length=50, choices=[('single', 'Single'), ('double', 'Double'), ('bedsitter', 'Bedsitter')])
    price_per_semester = models.DecimalField(max_digits=8, decimal_places=2)
    available_rooms = models.IntegerField()

    def __str__(self):
        return f"{self.room_name} - {self.hostel.name}"


class RoomImage(models.Model):
    room_type = models.ForeignKey(RoomType, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/rooms')

    def __str__(self):
        return f"Image for {self.room_type.room_name} in {self.room_type.hostel.name}"


class Booking(models.Model):
    SINGLE = 'Single'
    DOUBLE = 'Double'
    BEDSITTER = 'Bedsitter'

    ROOM_TYPE_CHOICES = [
        (SINGLE, 'Single'),
        (DOUBLE, 'Double'),
        (BEDSITTER, 'Bedsitter'),
    ]

    # Personal Information
    full_name = models.CharField(max_length=50)
    admission_number = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()
    semester = models.CharField(max_length=50)

    # Emergency Contact Information
    emergency_name = models.CharField(max_length=50)
    emergency_phone = models.CharField(max_length=15)
    emergency_relationship = models.CharField(max_length=20)

    # Room Details
    hostel = models.ForeignKey('Hostel', on_delete=models.CASCADE, related_name="bookings")
    room_type = models.CharField(max_length=15, choices=ROOM_TYPE_CHOICES)

    # Transaction Details
    transaction_message = models.TextField(blank=True, null=True)

    # Verification
    verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Check if the `verified` field is being updated to True
        if self.pk:  # Only for existing records
            original = Booking.objects.get(pk=self.pk)
            if not original.verified and self.verified:  # Only if verification status changes to True
                # HTML Email Content
                email_content = format_html(
                    """
                    <div style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; overflow: hidden;">
                            <div style="background-color: #4CAF50; color: #ffffff; padding: 15px 20px; text-align: center;">
                                <img src="{logo_url}" alt="Unistay Logo" style="max-width: 150px;">
                                <h2 style="margin: 0;">Booking Confirmation</h2>
                            </div>
                            <div style="padding: 20px;">
                                <p style="font-size: 16px; color: #333;">
                                    Dear <strong>{full_name}</strong>,
                                </p>
                                <p style="font-size: 14px; color: #555;">
                                    We are thrilled to confirm your booking at <strong>{hostel_name}</strong>. Below are your booking details:
                                </p>
                                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #555;">Room Type:</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #333;">{room_type}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #555;">Transaction Details:</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #333;">{transaction_message}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #555;">Booking Date:</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #333;">{booking_date}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #555;">Booking Time:</td>
                                        <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #333;">{booking_time}</td>
                                    </tr>
                                </table>
                                <p style="font-size: 14px; color: #555; margin-top: 15px;">
                                    Thank you for choosing Unistay. Enjoy exclusive discounts on future bookings with our referral program!
                                </p>
                                <p style="font-size: 14px; color: #555; margin-top: 15px;">
                                    Best regards,<br>
                                    <strong>Unistay Team</strong>
                                </p>
                            </div>
                            <div style="background-color: #f9f9f9; padding: 10px 20px; text-align: center;">
                                <p style="font-size: 12px; color: #999;">Follow us on:</p>
                                <a href="https://facebook.com/unistay" style="margin: 0 10px; text-decoration: none;">
                                    <img src="{facebook_icon_url}" alt="Facebook" style="width: 24px;">
                                </a>
                                <a href="https://twitter.com/unistay" style="margin: 0 10px; text-decoration: none;">
                                    <img src="{twitter_icon_url}" alt="Twitter" style="width: 24px;">
                                </a>
                                <a href="https://instagram.com/unistay" style="margin: 0 10px; text-decoration: none;">
                                    <img src="{instagram_icon_url}" alt="Instagram" style="width: 24px;">
                                </a>
                            </div>
                        </div>
                    </div>
                    """,
                    logo_url="https://yourwebsite.com/static/logo.png",
                    facebook_icon_url="https://yourwebsite.com/static/icons/facebook.png",
                    twitter_icon_url="https://yourwebsite.com/static/icons/twitter.png",
                    instagram_icon_url="https://yourwebsite.com/static/icons/instagram.png",
                    full_name=self.full_name,
                    hostel_name=self.hostel.name,
                    room_type=self.room_type,
                    transaction_message=self.transaction_message,
                    booking_date=self.created_at.strftime('%B %d, %Y'),
                    booking_time=self.created_at.strftime('%I:%M %p'),
                )

                # Send Email
                send_mail(
                    subject="🎉 Booking Confirmation - Unistay",
                    message="Your booking confirmation details.",  # Plain text fallback
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.email],
                    html_message=email_content,  # HTML version of the email
                    fail_silently=False,
                )
        # Save the changes
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.hostel.name}"

    class Meta:
        ordering = ['-created_at']  # Show recent bookings first
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"


class StudentProfile(models.Model):
    # Link to User model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Basic Information
    full_name = models.CharField(max_length=50, blank=True, null=True)
    admission_number = models.CharField(max_length=20, blank=True, null= True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Verification
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


def generate_verification_code():
    """Generates a random 6-digit verification code."""
    return str(random.randint(100000, 999999))





def send_verification_email(self, request):
        """Send the verification email with the verification code."""
        verification_link = f"{request.scheme}://{request.get_host()}{reverse('verification')}?user_id={self.user.pk}&code={self.verification_code}"
        subject = 'Account Verification'
        
        # Render the email content using the template
        message = render_to_string('verification_email.html', {
            'user': self.user,
            'verification_link': verification_link,
        })
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email])




# Payment Method model
class PaymentMethod(models.Model):
    PAYMENT_CHOICES = [
        ('send_money', 'Send Money'),
        ('buy_goods', 'Buy Goods (Till Number)'),
        ('paybill', 'Paybill'),
    ]

    hostel = models.ForeignKey(Hostel, related_name='payment_methods', on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    send_money = models.CharField(max_length=20, blank=True, null=True)
    paybill_number = models.CharField(max_length=20, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    till_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.hostel.name} - {self.get_payment_type_display()}"


# Transaction model
class Transaction(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='transaction')
    transaction_message = models.TextField()
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transaction for {self.booking} - Verified: {self.is_verified}"

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
