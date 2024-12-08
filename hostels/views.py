
import random
import string
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .forms import BookingForm
from .models import Hostel, RoomType, StudentProfile, generate_verification_code
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .forms import CustomUserCreationForm
from django.http import Http404
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from .forms import StudentProfileForm
from .models import StudentProfile






def index(request):
    # Fetch all hostels to display
    hostels = Hostel.objects.all()
    
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get the user's profile if it exists
        try:
            studentprofile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            studentprofile = None  # If no profile exists, set it to None
    else:
        studentprofile = None  # If the user is not logged in, no profile data
    
    return render(request, 'index.html', {
        'hostels': hostels,
        'studentprofile': studentprofile  # Pass the profile to the template
    })

@login_required
def home_view(request):
    hostels = Hostel.objects.all()

    # Fetch the student profile of the logged-in user
    try:
        studentprofile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        studentprofile = None  # Handle case where profile doesn't exist

    # Pass both hostels and the student profile to the template
    return render(request, 'home.html', {
        'hostels': hostels,
        'studentprofile': studentprofile,
        'user': request.user,
    })





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





@login_required
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






def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))

\

def send_verification_email(user_email, verification_code, request):
    """Send a styled verification email to the user."""
    
    # HTML content for the email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .email-header img {{
                max-width: 100px;
                margin-bottom: 10px;
            }}
            .email-body {{
                padding: 30px;
                text-align: center;
            }}
            .verification-code {{
                display: inline-block;
                background: #f8f8f8;
                border: 2px dashed #4CAF50;
                padding: 20px 40px;
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                margin: 20px 0;
            }}
            .email-footer {{
                background-color: #f4f4f4;
                color: #666;
                padding: 10px 20px;
                text-align: center;
                font-size: 12px;
            }}
            a.button {{
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
                font-size: 16px;
                margin-top: 20px;
            }}
            a.button:hover {{
                background: #45a049;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <!-- Header Section -->
            <div class="email-header">
                <img src="http://0.0.0.0:8000/static/image/logo.png" alt="Site Logo">
                <h1>Account Verification</h1>
            </div>
            <!-- Body Section -->
            <div class="email-body">
                <p>Hello,</p>
                <p>Thank you for registering on our platform. To complete your registration, please verify your account using the code below:</p>
                <div class="verification-code">{verification_code}</div>
               
            </div>
            <!-- Footer Section -->
            <div class="email-footer">
                <p>If you did not request this, please ignore this email.</p>
                <p>&copy; 2024 Unistay. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Fallback plain-text content
    text_content = strip_tags(f"""
    Verify Your Account
    Your verification code is {verification_code}.
    
    """)

    # Send the email
    email = EmailMultiAlternatives(
        subject="Account Verification",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()



def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()  # Save the user object before creating the profile

            # Generate and save the verification code
            verification_code = generate_verification_code()
            profile = user.studentprofile  # Assuming you've set up the StudentProfile model
            profile.verification_code = verification_code
            profile.save()

            # Send the verification email
            send_verification_email(user.email, verification_code, request)

            # Redirect to the verification page with the user_id in the URL
            return redirect(f'/verification/?user_id={user.pk}')  # Include user_id in the URL

    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})



def verification(request):
    # Retrieve `user_id` or `code` from the query string
    user_id = request.GET.get('user_id')
    code = request.GET.get('code')

    # Ensure at least one identifier is provided
    if not user_id and not code:
        raise Http404("User ID or verification code is required")

    try:
        # Find the user by `user_id` or `code`
        if user_id:
            user = User.objects.get(pk=user_id)
        elif code:
            user = User.objects.get(studentprofile__verification_code=code)

        student_profile = user.studentprofile
    except User.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect('register')  # Redirect to the registration page
    except StudentProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('register')  # Redirect if no student profile is found

    if request.method == "POST":
        entered_code = request.POST.get('verification_code')

        if entered_code == student_profile.verification_code:
            # Mark the user as verified
            student_profile.is_verified = True
            student_profile.save()

            # Log the user in
            login(request, user)
            messages.success(request, "Your account has been successfully verified!")
            return redirect('home')  # Redirect to home page or desired location
        else:
            messages.error(request, "Invalid verification code. Please try again.")

    # Pass `user_id` to the template for rendering
    return render(request, 'verify_email.html', {'user_id': user.id})

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







@login_required
def update_profile(request):
    # Get the student's profile or create it if it doesn't exist
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Add a success message
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('home')  # Redirect to the home page or profile page
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, 'update_profile.html', {'form': form, 'user_profile': profile})