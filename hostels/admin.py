from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Amenity,
    Hostel,
    RoomType,
    RoomImage,
    Booking,
    StudentProfile,
    PaymentMethod,
    Transaction,
)



# Amenity Admin
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Ensure all fields exist in the model
    search_fields = ('name',)


# Hostel Admin
@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'total_rooms')  # Ensure fields exist
    search_fields = ('name', 'location')
    list_filter = ('location',)
    readonly_fields = ('id',)


# Room Type Admin
@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_name', 'hostel', 'price_per_semester', 'available_rooms')
    search_fields = ('room_name', 'hostel__name')
    list_filter = ('room_name', 'hostel')


# Room Image Admin
@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_type', 'image')
    search_fields = ('room_type__room_name', 'room_type__hostel__name')


# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'admission_number',
        'hostel',
        'room_type',
        'contact_number',
        'email', 
        'created_at',
        'truncated_transaction',
        'verified', 
        
    )
    list_editable = ('verified',)
    search_fields = (
        'full_name',
        'admission_number',
        'email',
        'contact_number',
        'hostel__name',
        'emergency_name',
    )
    list_filter = (
        'hostel',
        'room_type',
        'verified',
        'created_at',
    )
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'full_name',
                'admission_number',
                'contact_number',
                'email',
                'semester',
            ),
        }),
        ('Emergency Contact Information', {
            'fields': (
                'emergency_name',
                'emergency_phone',
                'emergency_relationship',
            ),
        }),
        ('Room Details', {
            'fields': (
               
                'room_type',
                
            ),
        }),
        ('Transaction Details', {
            'fields': (
                'transaction_message',
                'verified',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    ordering = ['-created_at']

    def display_verified(self, obj):
        """Custom display for verified status with icons."""
        if obj.verified:
            return format_html('<span style="color: green;">✔</span>')
        return format_html('<span style="color: red;">✘</span>')

    display_verified.short_description = 'Verified'  # Column header
    display_verified.admin_order_field = 'verified'  # Allows sorting by verified

    def truncated_transaction(self, obj):
        return obj.transaction_message[:50] + '...' if len(obj.transaction_message) > 50 else obj.transaction_message
    truncated_transaction.short_description = 'Transaction Message' 


# Student Profile Admin
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_number', 'is_verified', 'verification_code')
    search_fields = ('user__username', 'verification_code')
    list_filter = ('is_verified',)
    ordering = ('user',)
    
    # Customize form layout in detail view
    fieldsets = (
        (None, {
            'fields': ('user', 'contact_number', 'verification_code', 'is_verified')
        }),
    )



# Payment Method Admin
@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'hostel', 'payment_type', 'till_number', 'paybill_number')
    search_fields = ('hostel__name', 'payment_type')
    list_filter = ('payment_type',)


# Transaction Admin
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'is_verified', 'verification_date')
    search_fields = ('booking__full_name', 'transaction_message')
    list_filter = ('is_verified', 'verification_date')
    readonly_fields = ('verification_date',)
    date_hierarchy = 'verification_date'
