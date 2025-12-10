from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect 
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from api.models import User, Train, Booking, Stop
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.contrib import messages




# Create your views here.

#admin login page view
@csrf_protect
@never_cache
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("adminhome")
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("adminhome")
            request.session.flush()
        else:
            error = "Invalid credentials or not an admin user."
            return render(request, "admin.html", {'error': error})
    return render(request,"admin.html")    
    
@csrf_protect
@login_required(login_url='login')
@never_cache
def admin_home(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("login")
    trains = Train.objects.all()
    bookings = Booking.objects.all()
    context = {
        'trains': trains,
        'bookings': bookings,
    }
    return render(request, "admin_home.html", context)

@login_required(login_url='login')
def edit_train(request, id):
    train = get_object_or_404(Train, id=id)

    if request.method == "POST":
        train.train_name = request.POST.get("train_name")
        train.train_number = request.POST.get("train_number")
        train.from_place = request.POST.get("from_place")
        train.to_place = request.POST.get("to_place")
        train.departure_time = request.POST.get("departure_time")
        train.arrival_time = request.POST.get("arrival_time")
        train.ticket_price = request.POST.get("ticket_price")
       
        train.total_seats = request.POST.get("total_seats")
        train.available_seats = request.POST.get("available_seats")
        train.is_active = request.POST.get("is_active") == "True"
        
        train.save()
        return redirect("adminhome")

    return render(request, "edit_train.html", {"train": train})



@login_required(login_url='login')
def delete_train(request, id):
    train = get_object_or_404(Train, id=id)
    train.delete()
    return redirect("adminhome")
@login_required(login_url='login')
def add_train(request):
    if request.method == "POST":
         # Check if a train with this number already exists
        train_number = request.POST.get("train_number")
        if Train.objects.filter(train_number=train_number).exists():
            messages.error(request, "Train number already exists!")
            return redirect("add_train")

        Train.objects.create(
            train_name = request.POST.get("train_name"),
            train_number = train_number,
            from_place = request.POST.get("from_place"),
            to_place = request.POST.get("to_place"),
            departure_time = request.POST.get("departure_time"),
            arrival_time = request.POST.get("arrival_time"),
            ticket_price = request.POST.get("ticket_price"),
          
            total_seats = request.POST.get("total_seats"),
            available_seats = request.POST.get("available_seats"),
            is_active = request.POST.get("is_active") == "True"
        )
       

        return redirect("adminhome")

    return render(request, "add_train.html")


@csrf_protect
@login_required(login_url='login')
@never_cache

def logout_admin(request):
    request.session.flush()
    logout(request)

    return redirect("login")


@csrf_protect
@login_required(login_url='login')
@never_cache
def train_stops(request, train_id):
    train = get_object_or_404(Train, id=train_id)
    stops = train.stops.order_by("order")

    return render(request, "train_stops.html", {
        "train": train,
        "stops": stops,
    })
@csrf_protect
@login_required(login_url='login')
@never_cache
def add_stop(request, train_id):
    train = get_object_or_404(Train, id=train_id)

    if request.method == "POST":
        stop_name = request.POST["stop_name"]
        fare = request.POST["fare_from_previous"]
        order = request.POST["order"]

        Stop.objects.create(
            train=train,
            stop_name=stop_name,
            fare_from_previous=fare,
            order=order
        )

        return redirect("train_stops", train_id=train.id)

    return render(request, "add_stop.html", {"train": train})
@csrf_protect
@login_required(login_url='login')
@never_cache
def delete_stop(request, stop_id):
    stop = get_object_or_404(Stop, id=stop_id)
    train_id = stop.train.id
    stop.delete()
    return redirect("train_stops", train_id=train_id)

@csrf_protect
@login_required(login_url='login')
@never_cache
def toggle_train_status(request, train_id):
    train = get_object_or_404(Train, id=train_id)
    train.is_active = not train.is_active  # Toggle True/False
    train.save()
    return redirect("adminhome")



@csrf_protect
@login_required(login_url='login')
@never_cache
def reports_home(request):
    return render(request, "reports_home.html")


@csrf_protect
@login_required(login_url='login')
@never_cache
def total_collection_by_date(request):
    date = request.GET.get("date")
    total = 0

    bookings = []

    if date:
        bookings = Booking.objects.filter(booking_date=date)
        total = sum(b.total_price for b in bookings)

    return render(request, "total_collection_by_date.html", {
        "bookings": bookings,
        "total": total,
        "selected_date": date
    })


@csrf_protect
@login_required(login_url='login')
@never_cache    
def train_collection_by_date(request):
    date = request.GET.get("date")
    train_id = request.GET.get("train_id")

    trains = Train.objects.all()
    bookings = []
    total = 0

    if date and train_id:
        bookings = Booking.objects.filter(booking_date=date, train_id=train_id)
        total = sum(b.total_price for b in bookings)

    return render(request, "train_collection_by_date.html", {
        "trains": trains,
        "bookings": bookings,
        "total": total,
        "selected_date": date,
        "selected_train": train_id,
    })
