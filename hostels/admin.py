from django.contrib import admin
from .models import Amenity, Hostel, PaymentMethod, Booking, RoomImage, RoomType, StudentProfile, Transaction

admin.site.register(Hostel)
admin.site.register(Booking)
admin.site.register(StudentProfile)
admin.site.register(PaymentMethod)
admin.site.register(Amenity)
admin.site.register(RoomType)
admin.site.register(RoomImage)

# Optional: Custom admin class to control display and features
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('booking', 'is_verified', 'verification_date')  # Fields to display in list view
    search_fields = ('booking__student__username', 'transaction_message')  # Enable search by fields
    list_filter = ('is_verified', 'verification_date')  # Filters for easy navigation

    # Optional: Inline editing of related models
    readonly_fields = ('verification_date',)  # Make fields read-only if desired
    date_hierarchy = 'verification_date' 