from django.conf import settings
from django.db import models




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
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    semester = models.CharField(max_length=50)

    # Emergency Contact Information
    emergency_name = models.CharField(max_length=50)
    emergency_phone = models.CharField(max_length=15)
    emergency_relationship = models.CharField(max_length=20)

    # Room Details
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="bookings")
    room_type = models.CharField(max_length=15, choices=ROOM_TYPE_CHOICES)
    

    # Transaction Details
    transaction_message = models.TextField(blank=False, null=False)
    verified = models.BooleanField(default=False) 
   
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)      

    def __str__(self):
        return f"{self.full_name} - {self.hostel.name}"
    class Meta:
        ordering = ['-created_at']  # Show recent bookings first
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"


# Optional: Student Profile model
class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use custom user model
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.email  # Return email instead of username


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
