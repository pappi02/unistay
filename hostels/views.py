from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .forms import BookingForm
from .models import Booking, Hostel, RoomType, StudentProfile, Transaction
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

def index(request):
    # Fetch all hostels to display 
    hostels = Hostel.objects.all()
    return render(request, 'index.html', {'hostels': hostels})



@login_required
def home_view(request):
    hostels = Hostel.objects.all()
    return render(request, 'home.html', {'hostels': hostels})  # Ensure you have a 'home.html' template





@login_required
def hostels_list(request):
    query = request.GET.get('search', '')  # Search query
    location = request.GET.get('location', '')  # Filter by location
    amenities = request.GET.getlist('amenities')  # Filter by amenities
    price_range = request.GET.get('price', '')  # Filter by price range

    hostels = Hostel.objects.all()

    if query:
        hostels = hostels.filter(name__icontains=query)
    if location:
        hostels = hostels.filter(location__icontains=location)
    if amenities:
        hostels = hostels.filter(amenities__name__in=amenities).distinct()
    if price_range:
        hostels = hostels.filter(room_types__price_per_semester__lte=price_range)

    hostels = hostels.order_by('name')  # Order for pagination consistency
    paginator = Paginator(hostels, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hostels_list.html', {
        'page_obj': page_obj,
        'search_query': query,
        'location_query': location,
        'amenities_query': amenities,
        'price_query': price_range,
    })






def booking_success(request):
    # Render the booking success page
    return render(request, 'booking_success.html')


def about(request):
    return render(request, 'about.html')



@login_required
def create_booking(request, hostel_id):
    # Fetch the hostel only once, regardless of request type (GET or POST)
    hostel = get_object_or_404(Hostel, id=hostel_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        
        if form.is_valid():
            # Save the booking to the database
            booking = form.save(commit=False)
            booking.hostel = hostel  # Associate the booking with the correct hostel
            booking.save()
            
            # Display success message
            messages.success(request, 'Booking created successfully.')
            return redirect('booking_success')  # Redirect to a success page (adjust URL name if needed)
        else:
            # If the form is invalid, show error messages
            messages.error(request, 'Please correct the errors below.')
    else:
        # For GET requests, initialize the form
        form = BookingForm()

    return render(request, 'create_booking.html', {
        'form': form,
        'hostel': hostel,  # Pass hostel context to the template
    })


def contact(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

       
        email_subject = f"New Contact Form Submission: {subject}"
        email_message = f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage:\n{message}"

        
        send_mail(
            email_subject,
            email_message,
            settings.EMAIL_HOST_USER,  # From email
            ['hushpappi2002@gmail.com'],    # To email 
            fail_silently=False,
        )

        try:
            validate_email(email)  
        except ValidationError:
            return HttpResponse("Invalid email format", status=400)
    
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')

    return render(request, 'contact.html')





def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Ensure the user is authenticated by email instead of username
        try:
            user = User.objects.get(email=email)  # Use email to retrieve the user
            if user is not None:
                # Authenticate the user manually by matching email and password
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    return redirect('home')  # Redirect to home page after successful login
                else:
                    messages.error(request, "Invalid email or password.")
                    return redirect('login')  # Redirect back to login on failure
            else:
                messages.error(request, "No user found with that email address.")
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "No user found with that email address.")
            return redirect('login')

    return render(request, 'login.html')





def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact_number = request.POST.get('contact_number')

        # Check if the user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "A user with that email already exists.")
            return redirect('register')

        # Create the user
        user = User.objects.create_user(username=email, email=email, password=password)

        # Check if StudentProfile already exists for this user
        if not hasattr(user, 'studentprofile'):
            # Create a StudentProfile instance
            StudentProfile.objects.create(user=user, contact_number=contact_number)

        # Log the user in
        login(request, user)
        messages.success(request, "Registration successful! You are now logged in.")
        return redirect('home')  # Redirect to the home page or any other page

    return render(request, 'register.html')




@login_required
def payment_method(request, hostel_id, room_type_id, price):
    # Fetch the hostel instance by ID
    hostel = get_object_or_404(Hostel, id=hostel_id)
    
    # Fetch the room type instance by ID
    room_type = get_object_or_404(RoomType, id=room_type_id)
    
    # Retrieve all payment methods associated with the hostel
    payment_methods = hostel.payment_methods.all()

    # Pass all relevant data to the template
    return render(request, 'payment_method.html', {
        'hostel': hostel,
        'room_type': room_type,
        'price': price,
        'payment_methods': payment_methods,
    })



def hostel_details(request, hostel_id):
    # Get the hostel object by ID
    hostel = get_object_or_404(Hostel, id=hostel_id)
    
    # Render the hostel details template
    return render(request, 'hostel_details.html', {'hostel': hostel})