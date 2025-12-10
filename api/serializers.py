from rest_framework import serializers
from .models import Train,User
from rest_framework import serializers
from .models import Booking

class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'






class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['email', 'name', 'phone_number', 'address', 'age', 'gender']



class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ['booking_id', 'user']
