from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import index, home_view, booking, confirm_booking, about, contact, login_view, register, payment_method

urlpatterns = [
    path('', index, name='index'),  # Homepage without login
    path('home/', home_view, name='home'),  # Home view that requires login
    path('booking/', booking, name='booking'),
    path('confirm_booking/', confirm_booking, name='confirm_booking'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('payment_method/<int:booking_id>/', payment_method, name='payment_method'),
    
]


# Correctly concatenate the static URL patterns to urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)