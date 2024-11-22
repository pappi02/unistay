from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from forms import BookingForm
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
def booking(request, hostel_id):
    # Get the hostel instance
    hostel = get_object_or_404(Hostel, id=hostel_id)
    
    # Initialize the form with pre-filled hostel name
    form = BookingForm(request.POST or None, initial={'hostel_name': hostel.id})
    
    if request.method == "POST":
        if form.is_valid():
            cleaned_data = form.cleaned_data
            try:
                # Fetch the room type instance using the room_type field
                room_type = get_object_or_404(RoomType, id=cleaned_data['room_type'])

                # Fetch transaction message
                transaction_message = request.POST.get('transaction_message', '')

                # Create a booking entry
                booking = Booking(
                    full_name=cleaned_data['full_name'],
                    admission_number=cleaned_data['admission_number'],
                    phone_number=cleaned_data['phone_number'],
                    email=cleaned_data['email'],
                    semester=cleaned_data['semester'],
                    emergency_name=cleaned_data['emergency_name'],
                    emergency_phone=cleaned_data['emergency_phone'],
                    emergency_relationship=cleaned_data['emergency_relationship'],
                    hostel=hostel,
                    room_type=room_type,
                    room_number=cleaned_data['room_number'],
                    transaction_message=transaction_message,
                    is_verified=False,
                )
                booking.save()

                # Add success message
                messages.success(request, "Booking submitted successfully for verification!")

                # Redirect to the success page
                return redirect('booking_success')  # Define this URL in your urls.py

            except Exception as e:
                print(f"Error: {e}")
                form.add_error(None, "There was an error processing your booking. Please try again.")
        else:
            form.add_error(None, "Please correct the errors below.")

    # Render the form with the pre-filled hostel name
    return render(request, 'booking.html', {'form': form, 'hostel': hostel})




def booking_success(request):
    return render(request, 'booking_success.html')




@login_required
def confirm_booking(request):
    if request.method == "POST":
        # Extract the form data
        hostel_name = request.POST.get('hostel_name')
        room_type = request.POST.get('room_type')
        transaction_message = request.POST.get('transaction_message')

        # Ensure all necessary data is present
        if not hostel_name or not room_type or not transaction_message:
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        try:
            # Use atomic transaction to ensure all steps succeed or fail together
            with transaction.atomic():
                # Retrieve the selected hostel and room
                hostel = Hostel.objects.get(name=hostel_name)
                room = RoomType.objects.get(hostel=hostel, room_type=room_type, is_available=True)

                # Create a booking
                booking = Booking.objects.create(
                    student=request.user,
                    room=room,
                    is_active=True  # We assume booking is active immediately
                )

                # Create a transaction record with the provided transaction message and unverified status
                Transaction.objects.create(
                    booking=booking,
                    transaction_message=transaction_message,
                    is_verified=False,  # Assume not verified until manual or automated verification
                )

                # Mark the room as unavailable since it's booked
                room.is_available = False
                room.save()

            return JsonResponse({'success': 'Booking confirmed and transaction recorded.'}, status=200)

        except Hostel.DoesNotExist:
            return JsonResponse({'error': 'Hostel not found.'}, status=404)
        except RoomType.DoesNotExist:
            return JsonResponse({'error': 'Room not available.'}, status=404)
        except Exception as e:
            # Catch any unforeseen errors
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    # If request method is not POST
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def about(request):
    return render(request, 'about.html')




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
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home after login
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')  # Redirect back to login on failure

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