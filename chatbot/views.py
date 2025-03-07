from django.shortcuts import render,redirect
from django.http import JsonResponse
import openai
import os
from dotenv import load_dotenv
from .models import Chat
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone


# Load environment variables
load_dotenv()

# Get API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')
# openai.api_key = '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'

def ask_openai(message):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4" if you have access
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        max_tokens=150,
        temperature=0.7
    )
    
    # Extract the response text
    answer = response.choices[0].message.content.strip()
    return answer
    # print(response)

def chatbot(request):
    chats=Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        try:
            response = ask_openai(message)
            chat=Chat(user=request.user,message=message,response=response, created_at=timezone.now())
            chat.save()
            return JsonResponse({'message': message, 'response': response})
        except Exception as e:
            return JsonResponse({'message': message, 'response': f"Error: {str(e)}"})
    
    return render(request, 'chatbot.html',{'chats':chats})

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(request,username=username , password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('chatbot')
        else:
            error_message='Invalid username or password'
            return render(request,'login.html',{'error_message':error_message})

    else:
        return render(request,'login.html')
    

def logout(request):
    auth.logout(request)
    return redirect('login')

def register(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password1=request.POST['password1']
        password2=request.POST['password2']

        if password1==password2:
            try:
                user=User.objects.create_user(username,email,password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')  ##put url name plz whats inside the name

            except: 
                error_message='Error creating account' 
                return render(request,'register.html', {'error_message':error_message})

        else:
            error_message='Password do not match'
            return render(request,'register.html', {'error_message':error_message})
    

    return render(request,'register.html')