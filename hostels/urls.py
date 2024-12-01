from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import index, home_view, contact, login_view, register, about
from hostels import views

urlpatterns = [
    path('', index, name='index'),  # Homepage without login
    path('home/', home_view, name='home'),  # Home view that requires login
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('payment_method/<int:hostel_id>/<int:room_type_id>/<price>/', views.payment_method, name='payment_method'),
    path('hostel/<int:hostel_id>/', views.hostel_details, name='hostel_details'),
    path('booking_success/', views.booking_success, name='booking_success'),
    path('hostels/', views.hostels_list, name='hostels_list'),
    path('create_booking/<int:hostel_id>/', views.create_booking, name='create_booking'),
    path('verification/', views.verification, name='verification'),
   
    
]


# Correctly concatenate the static URL patterns to urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)