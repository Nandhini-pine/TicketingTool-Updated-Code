from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime, time

def login(request):
    context = {}  # Initialize the context dictionary
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = None  # Initialize the user variable
        
        # Try to authenticate the user with the provided credentials
        if User.objects.filter(username=username).exists():
            user = auth.authenticate(username=username, password=password)
        else:
            user = User.objects.filter(email=username).first()
            if user:
                user = auth.authenticate(username=user.username, password=password)
        
        if user is not None:
            auth.login(request, user)

            # Get the store associated with the logged-in user

            try:
                user_store = user.profile.store
            except AttributeError:
                user_store = None  # Handle the case where the user doesn't have an associated store

            if user.groups.filter(name='StorePerson').exists():
                return redirect('base')
            elif user.groups.filter(name='Manager').exists():
                return redirect('Manager_base')
            elif user.groups.filter(name='Engineer').exists():
                return redirect('engineer_dashboard')
            elif user.groups.filter(name='Admin').exists():
                return redirect('admin_dashboard')

            return redirect('base')  # Default redirection if user doesn't have specific role

        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')  # Redirect back to the login page

    
    else:
        messages.get_messages(request)  # Clear any messages from previous requests
        
        # Determine the time of day and set the appropriate welcome message
        current_time = datetime.now().time()
        if current_time < time(12):
            welcome_message = "Good Morning"
            slogan = "Start your day with enthusiasm and productivity!"
        elif current_time < time(18):
            welcome_message = "Good Afternoon"
            slogan = "Stay focused and make the most of your afternoon!"
        else:
            welcome_message = "Good Evening"
            slogan = "Reflect on your day and plan for tomorrow's success."
        
        # Pass the welcome message and slogan to the template
        context['welcome_message'] = welcome_message
        context['slogan'] = slogan
        
        return render(request, "Login/index.html", context)



def logout(request):
    auth.logout(request)
    return redirect('login')  # Replace 'login' with the URL name of your login page