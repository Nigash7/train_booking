from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .models import User
from django.contrib.auth import authenticate
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK



@csrf_exempt
@api_view(['GET'])
@permission_classes([])
def demo(request):
    return Response({"message":"Demo API is working"},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((AllowAny,))
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
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def Login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'},status=HTTP_400_BAD_REQUEST)
    
    user = authenticate(Username=email, password=password)
    print(user)
   
    if not user:
        return Response({'error': 'Invalid Credentials'},status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},status=HTTP_200_OK)


# Create your views here.    
