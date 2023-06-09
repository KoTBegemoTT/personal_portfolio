from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from .forms import TodoForm
from .models import Todo


def home(request):
    return render(request, 'todo_app/home.html')


def logout_user(request):
    if request.method == 'POST':
        logout(request)
    return render(request, 'todo_app/home.html')


def signup_user(request):
    if request.method == 'GET':
        return render(request, 'todo_app/signup_user.html')
    elif request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
            except IntegrityError:
                return render(request, 'todo_app/signup_user.html', context={'error': 'This username is already exist'})
            login(request, user)
            return redirect('todo_app:current_todos')
        else:
            return render(request, 'todo_app/signup_user.html', context={'error': 'Passwords did not match'})


def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo_app/login_user.html')
    elif request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('todo_app:current_todos')
        else:
            return render(request, 'todo_app/login_user.html', context={'error': 'Username and password did not math'})


def create_todo(request):
    if request.method == 'GET':
        return render(request, 'todo_app/create_todo.html')
    elif request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('todo_app:current_todos')
        else:
            return render(request, 'todo_app/create_todo.html',
                          context={'error': 'Bad data inputed'})


def current_todos(request):
    todos = Todo.objects.filter(user=request.user, date_completion__isnull=True)
    return render(request, 'todo_app/current_todos.html', context={'todos': todos})


def completed_todos(request):
    todos = Todo.objects.filter(user=request.user, date_completion__isnull=False).order_by('date_completion')
    return render(request, 'todo_app/completed_todos.html', context={'todos': todos})


def view_todo(request, pk):
    todo = get_object_or_404(Todo, id=pk, user=request.user)
    if request.method == 'GET':
        return render(request, 'todo_app/view_todo.html', context={'todo': todo})
    elif request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('todo_app:current_todos')
        else:
            return render(request, 'todo_app/view_todo.html',
                          context={'todo': todo, 'error': 'bad info'})


def complete_todo(request, pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, id=pk, user=request.user)
        todo.date_completion = timezone.now()
        todo.save()
        return redirect('todo_app:current_todos')


def delete_todo(request, pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, id=pk, user=request.user)
        todo.delete()
        return redirect('todo_app:current_todos')


def repeat_todo(request, pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, id=pk, user=request.user)
        todo.pk = None
        todo.date_completion = None
        todo.save()
        return redirect('todo_app:current_todos')