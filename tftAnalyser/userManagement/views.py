from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from tftAnalyser.settings import MAX_LENGTH_USERNAME, MIN_LENGTH_USERNAME, MAX_LENGTH_PASSWORD, MIN_LENGTH_PASSWORD
from django.core.exceptions import ValidationError
from userManagement.forms import SignupForm
from userManagement.models import Favorite
from analyze.views import getStreams
import requests
from analyze.models import Summoner


# Create your views here.

### Comprueba si el Summoner ya esta en la lista de favoritos del usuario actual
def alreadyFavorited(request, summ):
	if request.user.is_authenticated:
	           user_favorites=Favorite.objects.filter(user=request.user, summoner=summ)
	           if not user_favorites:
	              return False
	           else:
	              return True
	else:
	   return False
	   
### Funcion usada para validar ciertos parametros
### sobre el usuario y la contraseña.
### Ya se hace una validacion inicial a traves de
### los campos del formulario, pero es solo del lado
### del cliente: aqui se valida del lado del servidor
### Es importante que los minimos y maximos definidos
### aqui coincidan con los del formulario
def validate_signup(username, password):
   if len(username)<MIN_LENGTH_USERNAME:
      raise ValidationError(('El nombre de usuario debe tener al menos {0} caracteres.').format(MIN_LENGTH_USERNAME))
   elif len(username)>MAX_LENGTH_USERNAME:
      raise ValidationError(('El nombre de usuario debe tener como máximo {0} caracteres.').format(MAX_LENGTH_USERNAME))
   elif len(password)<MIN_LENGTH_PASSWORD:
      raise ValidationError(('La contraseña debe tener al menos {0} caracteres.').format(MIN_LENGTH_PASSWORD))
   elif len(password)>MAX_LENGTH_PASSWORD:
      raise ValidationError(('La contraseña debe tener como máximo {0} caracteres.').format(MAX_LENGTH_PASSWORD))
   elif not any(char.isdigit() for char in password):
      raise ValidationError('La contraseña debe contener al menos un dígito.')
   elif not any(char.isalpha() for char in password):
      raise ValidationError('La contraseña debe contener al menos una letra.')  
      
def signup(request):
   if request.method == 'POST':
      # Si se pulso login no se registra, solo se loguea
      if request.POST['submit'] == 'Registrarse': 
         # En caso de que el usuario ya exista tirar error  
         if User.objects.filter(username=request.POST['username']).exists():
            signup_form=SignupForm()
            streams=getStreams(5)
            context={'streams':streams, 'signup_form':signup_form}
            return render(request, 'userManagement/signup_error.html', context)
         # Comprueba que los parametros son válidos
         try:
            validate_signup(request.POST['username'],request.POST['password'])
         except Exception as e:
            signup_form=SignupForm()
            streams=getStreams(5)
            context={'streams':streams, 'signup_form':signup_form, 'error':str(e)}
            return render(request, 'analyze/validation_error.html', context)
         # Registra al usuario
         user = User.objects.create_user(username=request.POST['username'],password=request.POST['password'])
         user.save()
      # Loguea al usuario
      user = authenticate(username=request.POST['username'], password=request.POST['password'])
      if user is not None:
         login(request, user)
         return redirect('/tft')
      # Tirar error si el login es invalido
      else:
         signup_form=SignupForm()
         streams=getStreams(5)
         context={'streams':streams, 'signup_form':signup_form}
         return render(request, 'userManagement/login_error.html', context)
         
def logout_view(request):
	logout(request)
	return redirect(request.GET['next'])
	
def favorites(request):
   # Solo muestra la lista si hay un usuario logueado
   if request.user.is_authenticated:
      curr_user=request.user
      # Obtiene los favoritos del usuario actual
      user_favorites=Favorite.objects.filter(user=curr_user)
      favorite_list=[]
      # Los mete en una lista y calcula el winrate para cada uno
      for entry in user_favorites:
         favorite_list.append(entry.summoner)
      for entry in favorite_list:
         entry.winrate=float(entry.wins * 100) / entry.losses
   else:
      favorite_list=None
   signup_form=SignupForm()
   streams=getStreams(5)
   context={'streams':streams, 'signup_form':signup_form, 'favorite_list':favorite_list}
   return render(request,'analyze/favorites.html', context)

### Las funciones añadir/borrar favoritos asumen que el summoner esta siempre
### en la BD local y que no hay dos con el mismo nombre
### No nos molestamos con mensajes de error elaborados ya que estos no se deberian
### mostrar normalmente a los usuarios
def add_favorites(request, user_name):
   if not request.user.is_authenticated:
      return HttpResponse('Se debe iniciar sesión para añadir favoritos', status=401)
   curr_user=request.user
   curr_summoner=Summoner.objects.filter(name=user_name)
   if not curr_summoner:
      ### No encuentra summoner en nuestra BD, muestra error
      return HttpResponse('No se encuentra el summoner a ser añadido en la BD', status=500)
   favorite=Favorite(user=curr_user, summoner= curr_summoner[0])
   favorite.save()
   return redirect('/tft/user/'+user_name)
    
def delete_favorites(request, user_name):
   if not request.user.is_authenticated:
      return HttpResponse('Se debe iniciar sesión para eliminar favoritos', status=401)
   curr_summoner=Summoner.objects.filter(name=user_name)
   if not curr_summoner:
      return HttpResponse('No se encuentra el summoner a ser eliminado en la BD', status=500)
   Favorite.objects.filter(user=request.user, summoner=curr_summoner[0]).delete()
   return redirect('/tft/user/'+user_name)

