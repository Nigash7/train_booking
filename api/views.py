from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .models import User,Train
from django.contrib.auth import authenticate
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from django.contrib.auth.models import User as DjangoUser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from .serializers import  TrainSerializer,UserProfileSerializer
from .models import User
from django.shortcuts import get_object_or_404
# ---
import uuid
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking
from .serializers import BookingSerializer
# ----------------------------------------------------------------
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from io import BytesIO
from django.utils import timezone

# from django.contrib.auth import get_user_model
# print(get_user_model().objects.all())




@csrf_exempt
@api_view(['GET'])
@permission_classes([])
def demo(request):
    return Response({"message":"Demo API is working"},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny,])
def Signup_user(request):
    name = request.data.get("name")
    email = request.data.get("email")
    password = request.data.get("password")
    phone_number = request.data.get("phone_number")
    address = request.data.get("address")
    age = request.data.get("age")
    gender = request.data.get("gender")

    # Validate fields
    if not all([name, email, password, phone_number, address, age, gender]):
        return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({'message': 'Email already exists'}, status=400)

    # Create User
    user = User.objects.create_user(
        email=email,
        password=password,
        name=name,
        phone_number=phone_number,
        address=address,
        age=age,
        gender=gender
    )

    user.save()
    return JsonResponse({'message': 'User created successfully'}, status=200)
# ---------------------------------------------------------------------------------------------------------
#login 
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny,])
def Login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'},status=HTTP_400_BAD_REQUEST)
    print(email, password)
    user = authenticate(email=email, password=password)
    print(user)
   
    if not user:
        return Response({'error': 'Invalid Credentials'},status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},status=HTTP_200_OK)

#logout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)

# Train list 
@api_view(['GET'])
@permission_classes([AllowAny,])
def get_Train(request):
    train = Train.objects.all()
    serializer =TrainSerializer(train,many = True)
    return Response(serializer.data)
   
@api_view(['GET'])
@permission_classes([AllowAny,])
def get_Train_id(request,T_id):
   train=get_object_or_404(Train,id=T_id)
   serializer=TrainSerializer(train)
   return Response(serializer.data)   







# profile view
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)


# update profile

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user  # logged-in user
    
    serializer = UserProfileSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Profile updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# book ticket

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_ticket(request):
    train_id = request.data.get("train_id")
    seats = int(request.data.get("seats", 1))
    passenger_name = request.data.get("passenger_name")
    passenger_age = request.data.get("passenger_age")
    passenger_gender = request.data.get("passenger_gender")
    booking_date = request.data.get("booking_date")
    


    # Validate required fields
    if not all([train_id, seats, passenger_name, passenger_age, passenger_gender]):
        return Response({"message": "All fields are required"}, status=400)

    train = get_object_or_404(Train, id=train_id)

    if train.available_seats < seats:
        return Response({"message": "Not enough seats available"}, status=400)

    # Generate unique booking ID
    booking_id = "BK" + str(uuid.uuid4().hex[:8]).upper()

    # Price calculation
    total_price = seats * train.ticket_price

    # Save Booking
    booking = Booking.objects.create(
        user=request.user,
        train=train,
        booking_id=booking_id,
        seats=seats,
        passenger_name=passenger_name,
        passenger_age=passenger_age,
        passenger_gender=passenger_gender,
        total_price=total_price,
        booking_date=timezone.now(),
        travel_datetime=train.departure_time,
        
         
    )

    # Reduce available seats
    train.available_seats -= seats
    train.save()

    # Send confirmation email
    send_mail(
        subject="Train Ticket Booking Confirmation",
        message=f"Your ticket has been booked.\nBooking ID: {booking_id}\n Train: {train.train_name}\nSeats: {seats}\nTotal Price: ₹{total_price}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False,
    )

    return Response({
        "message": "Booking successful",
        "booking_id": booking_id,
        "booking_details": BookingSerializer(booking).data
    }, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data, status=200)

# download ticket as PDF
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # ===== HEADER SECTION =====
    p.setFillColorRGB(0.2, 0.4, 0.8)  # Blue top bar
    p.rect(0, height - 80, width, 80, fill=True, stroke=False)

    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 26)
    p.drawString(40, height - 50, "TRAIN TICKET")

    # ---- Sub Heading ----
    p.setFont("Helvetica", 12)
    p.drawString(40, height - 70, "Your Journey Details")

    # ===== TICKET BOX =====
    p.setFillColorRGB(0, 0, 0)
    p.setLineWidth(2)
    p.roundRect(30, height - 500, width - 60, 400, 20, stroke=True, fill=False)

    y = height - 120
    left_x = 50

    # ===== BOOKING DETAILS =====
    p.setFont("Helvetica-Bold", 14)
    p.drawString(left_x, y, "Booking Information")
    p.line(left_x, y - 5, width - 50, y - 5)

    p.setFont("Helvetica", 12)
    y -= 30
    p.drawString(left_x, y, f"Booking ID: {booking.booking_id}")
    y -= 20
    p.drawString(left_x, y, f"Booking Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}")

    # ===== PASSENGER DETAILS =====
    y -= 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(left_x, y, "Passenger Details")
    p.line(left_x, y - 5, width - 50, y - 5)

    p.setFont("Helvetica", 12)
    y -= 30
    p.drawString(left_x, y, f"Name: {booking.passenger_name}")
    y -= 20
    p.drawString(left_x, y, f"Age: {booking.passenger_age}")
    y -= 20
    p.drawString(left_x, y, f"Gender: {booking.passenger_gender}")
    y -= 20
    p.drawString(left_x, y, f"Seats Booked: {booking.seats}")

    # ===== TRAIN DETAILS =====
    y -= 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(left_x, y, "Train Details")
    p.line(left_x, y - 5, width - 50, y - 5)

    p.setFont("Helvetica", 12)
    y -= 30
    p.drawString(left_x, y, f"Train: {booking.train.train_name}")
    y -= 20
    p.drawString(left_x, y, f"Route: {booking.train.from_place} → {booking.train.to_place}")

    # Split date & time from DateTimeField
    departure_date = booking.train.departure_time.strftime("%d-%m-%Y")
    departure_time = booking.train.departure_time.strftime("%I:%M %p")

    y -= 20
    p.drawString(left_x, y, f"Departure Date: {departure_date}")
    y -= 20
    p.drawString(left_x, y, f"Departure Time: {departure_time}")

    y -= 20
    p.drawString(left_x, y, f"Total Price: ₹{booking.total_price}")


    # status payment
    payment_status = "Payment Status: Cash Payment at Station"

    p.setFont("Helvetica-Bold", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width / 2, 80, payment_status)

    # ===== FOOTER =====
    p.setFillColorRGB(0.2, 0.4, 0.8)
    p.rect(0, 0, width, 50, fill=True, stroke=False)

    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, 20, "Thank you for booking with us. Have a safe journey!")

    # ===== SAVE =====
    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


# Create your views here.    
