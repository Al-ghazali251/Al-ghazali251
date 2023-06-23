from django.shortcuts import render,redirect
from . forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import openai
import json
from . models import RecentChats
from datetime import date, timedelta


open_ai_key = "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"
openai.api_key = open_ai_key
# Create your views here.

@login_required(login_url='signin')
def index(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    seven_days_ago = date.today() - timedelta(days=7)
    
    questions = RecentChats.objects.filter(user=request.user)
    t_questions = questions.filter(created=today)
    y_questions = questions.filter(created=yesterday)
    s_questions = questions.filter(created__gte=seven_days_ago, created__lte=today)
    
    context = {"t_questions":t_questions, "y_questions": y_questions, "s_questions": s_questions}

    return render(request, "chatapp/index.html",context)


def signup(request):
    if request.user.is_authenticated:
        return redirect("index")
    
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST["username"]
            password = request.POST["password1"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            
            
            
    context = {"form": form}
    return render(request, "chatapp/signup.html", context)


def signin(request):
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == 'POST':
        
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
    
        else:
            error = "Invalid login details"
            context = {"error":error}
            return render(request,"chatapp/signin.html",context)

    context = {}
    return render (request,"chatapp/signin.html",context)



def signout(request):
    logout(request)
    return redirect("signin")



def getvalue(request):
    data = json.loads(request.body)
    message = data["msg"]
    response = ask_me(message)
    RecentChats.objects.create(user=request.user,question=message,answer=response)
    
    return JsonResponse({"msg":message, "res":response})


 
def ask_me(message):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
            
        ]
    
     )
   
    answer = response['choices'][0]['message']['content']
    # print(answer)   
    return answer
    