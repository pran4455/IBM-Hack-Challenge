from django.shortcuts import render
from django.shortcuts import redirect
from .models import User

# Create your views here.

def home(request):
    return render(request, "login.html")

def signup(request):

    if request.method == 'POST':
        print(request.POST)
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']  # Remember to hash the password before saving

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=password
        )
        # Redirect to login page or any other page you want
        return redirect('login')
    return render(request, 'signup.html')

def login(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            if user.password == password:
                # Successful login
                # You can redirect to the user's dashboard or any other page
                return redirect('dashboard')
            else:
                # Incorrect password
                return render(request, 'login.html', {'error_message': 'Incorrect password'})
        except User.DoesNotExist:
            # User does not exist
            return render(request, 'login.html', {'error_message': 'User does not exist'})

    return render(request, 'login.html')

def dashboard(request):

    return render(request, 'dashboard.html')

def forgotpass(request):

    return render(request, 'verify_otp.html')

def get_email(request):
    if request.method == "POST":
        email = request.POST["email"]
        with open("register.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            if email not in [row[3] for row in reader]:
                return render(
                    request, "forgot_password.html", {"message": "Email not found!"}
                )
            else:
                name = ""
                for row in reader:
                    if row[3] == email:
                        name = row[0]
                        break
                request.session["RESET_EMAIL"] = email
                request.session["RANDOM_OTP"] = random.randint(100000, 999999)
                subject = "OTP Verification for Resetting your Password"
                to = email
                content = (
                        """Hello """
                        + str(name)
                        + """, This mail is in response to your request of resetting your clinic account password. 

                                    Please enter or provide the following OTP: """
                        + str(request.session["RANDOM_OTP"])
                        + """

                                    Note that this OTP is valid only for this instance. Requesting another OTP will 
                                    make this OTP invalid. Incase you haven't requested to reset your password, 
                                    contact your xyz. Thank You """
                )

                send_email.send_email(to, subject, content)
                

                return render(request, "validate_otp.html")
    return render(request, "forgot_password.html")

def validate_otp(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm-password"]
        if password != confirm_password:
            return render(
                request,
                "validate_otp.html",
                {"alertmessage": "Passwords do not match!"},
            )
        elif int(otp) != request.session["RANDOM_OTP"]:
            return render(
                request, "validate_otp.html", {"alertmessage": "Incorrect OTP!"}
            )
        else:
            with open("register.csv", "r") as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                for idx, row in enumerate(rows):
                    if row[3] == request.session["RESET_EMAIL"]:
                        request.session["RESET_EMAIL"] = ""
                        rows[idx][4] = password
                        break
            csvfile.close()
            with open("register.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)
            csvfile.close()
            return render(
                request, "index.html", {"alertmessage": "Reset Password Successful!"}
            )
    else:
        return render(request, "validate_otp.html")

def verify_otp(request):

    return render(request, 'verify_otp.html')
