from django.shortcuts import render, redirect
from django.http import HttpResponse 
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ValidationError
import json
import math
from threading import Lock
import threading
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from analyze.models import Unit,Item,Trait,Summoner,Match,MatchTrait,MatchUnit,Top,AnalyzeUnit,AnalyzeTrait,AnalyzeObject
from userManagement.forms import SignupForm
from pandas import DataFrame, Series
import pandas
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import urllib
import requests

import analyze.utils as utils
import analyze.database as db_comm
import analyze.analisis as ana


# Create your views here.




# Youtube API
#"key": "AIzaSyC4Ccid1Ez1p1MKVu2sYrfgg38TkAa4M_k"


####  All sites that inherit from base.html should be given the
####  streams array given by this function as context so that
####  the twitch streams list works everywhere
def getStreams(amount):
   # Primero generamos un token de autenticacion
   oauth_params={'client_id':'YOUR-CLIENT-ID', 'client_secret':'YOUR-CLIENT-SECRET', 'grant_type':'client_credentials'}
   oauth_answer = requests.post("https://id.twitch.tv/oauth2/token",params=oauth_params)
   json_oauth_token=json.loads(oauth_answer.text)
   # Ahora declaramos los parametros y headers de la peticion principal
   getstreams_headers={"Authorization":"Bearer "+json_oauth_token["access_token"], 'Client-ID':'YOUR-CLIENT-ID'}
   getstreams_parameters={'game_id':'513143','language':'es','first':amount}
   getstreams_answer = requests.get("https://api.twitch.tv/helix/streams",headers=getstreams_headers,params=getstreams_parameters)
   # Finalmente eliminamos el token
   revoke_oauth_params={'client_id':'YOUR-CLIENT-ID', 'token':json_oauth_token["access_token"]}
   requests.post('https://id.twitch.tv/oauth2/revoke',params=revoke_oauth_params)
   # Ahora generamos la lista streams y la devolvemos
   if (getstreams_answer.status_code==200):
      json_answer = json.loads(getstreams_answer.text)
      json_list = json_answer["data"]
      streams = []
      for entry in json_list:
          parameters=[entry["user_name"],entry["title"],entry["thumbnail_url"].replace('{width}x{height}','178x100')]
          streams.append(parameters)
   else:
      print("Hubo un error al recuperar los streams de Twitch")
      streams=[]
   return streams

#/tft/
def tft(request):
   stream_amount=5
   signup_form=SignupForm()
   streams=getStreams(stream_amount)
   user_searched=request.GET.get('user', '')
   context={'streams':streams, 'signup_form':signup_form}
   if (user_searched!=''):
      return redirect('/tft/user/'+user_searched)
   return render(request,'analyze/tft.html', context)

#/tft/top
def top(request):
	controller = utils.Controller()
	controller.top_lock.acquire()
	#We dont want to ask the api each request, since they will return mostly the same
	#We update our local top database each 5 minutes 
	if( controller.top_last_update < (datetime.now() - timedelta(seconds= 5 * 60)) ):
		#publish the update and ask api
		controller.update_top_time()
		controller.top_lock.release()
		answer = requests.get('https://euw1.api.riotgames.com/tft/league/v1/challenger', headers=utils.RIOT_HEADER)
		# if api returns OK process the answer and use 
		# a different thread to update the database
		if (answer.status_code == 200):
			json_answer = json.loads(answer.text)
			json_list = json_answer["entries"]
			if not json_list:
				answer = requests.get('https://euw1.api.riotgames.com/tft/league/v1/master', headers=utils.RIOT_HEADER)
				json_answer = json.loads(answer.text)
				json_list = json_answer["entries"]
			top_list = []
			# Usar una thread da error "database is locked"
			# cuando la plantilla trata de hacer user.is_authenticated,
			# ya que haciendo esto en una thread la plantilla siempre
			# se muestra antes de que acabe la operación
			#thread_DB = threading.Thread(target=db_comm.update_Top, args=(json_list,))
			#thread_DB.start()
			###### Workaround temporal
			db_comm.update_Top(json_list)
			for summ in json_list:
				top_list.append(Top(summoner_id=summ["summonerId"], name=summ["summonerName"], league_points=summ["leaguePoints"], wins=summ["wins"], losses=summ["losses"]))
			top_list.sort(key=utils.sort_tops)
			if(len(top_list) > 20):
				top_list = top_list[:20]
		#else get the local copy
		else:
			top_list=Top.objects.all().order_by('-league_points', 'name')[:20]
	else:
		controller.top_lock.release()
		top_list=Top.objects.all().order_by('-league_points', 'name')[:20]
	#add extra informacion to display
	place = 1
	for s in top_list:
		s.winrate= float(s.wins * 100) / s.losses
		s.place = place
		place = place + 1
	#get things base.html needs in the context
	signup_form=SignupForm()
	streams=getStreams(5)
	context={'top_list':top_list,'streams':streams, 'signup_form':signup_form}
	return render(request, 'analyze/top.html', context)

#/tft/units
def units(request):
	un_list = []
	controller = utils.Controller()
	controller.units_lock.acquire()

	if( controller.units_last_update < (datetime.now() - timedelta(seconds= 24 * 3600)) ):
		controller.update_units_time()
		controller.units_lock.release()
		#create my global index
		g_index = utils.get_units_index()

		#create the DataFrame with that index
		df = DataFrame(index=g_index, dtype=np.int8)
		df_counter = 1

		#pick tops from my DB
		top_list = []
		try:
			top_list = Top.objects.all()
		except:
			pass

		#for each top get its last 20 games
		#and create a Series for each game
		for t in top_list:
			try:
				s=Summoner.objects.get(name=t.name)
				raw_match_list=Match.objects.filter(puuid=s.puuid).order_by("-match_id")[:20]
				for m in raw_match_list:
					unit_list = MatchUnit.objects.filter(puuid=s.puuid, match_id=m.match_id)
					serie = Series(index=g_index)
					for u in unit_list:
						serie[u.unit] = m.placement
					df[df_counter] = serie
					df_counter = df_counter + 1
			except:
				pass

		un_list = ana.analyze_full_dataframe(df, g_index)
		#update the database
		thread_DB = threading.Thread(target=db_comm.update_units, args=(un_list,))
		thread_DB.start()
	else:
		controller.units_lock.release()
		aux_un_list=AnalyzeUnit.objects.all()
		for unit in aux_un_list:
			un_list.append({
				"id" : unit.name.lower(),
				"name" : unit.name,
				"games" : unit.games,
				"mean" : unit.mean,
				"first" : unit.first,
				"top4" : unit.top,
				"losses" : unit.losses,
				})
	#build the context
	un_list.sort(key=utils.sort_by_games)
	place =1
	for un in un_list:
		un['place']= place
		place = place + 1
	#thing needed by base.html
	signup_form=SignupForm()
	streams=getStreams(5)
	context={'un_list':un_list,'streams':streams, 'signup_form':signup_form}
	return render(request, 'analyze/units.html', context)

#/tft/user/{user_name}/refresh	
#Each games takes arround 30 segs so 20*30s = 10 min
#can't paralelize because of DB
def refresh(request, user_name):
	puuid = None
	try:
		summ = Summoner.objects.get(name=user_name)
		puuid = summ.puuid
	except:
		pass
	#if no user in DB throw error
	if not puuid:
		context={'streams':getStreams(5), 'signup_form':SignupForm(), 'error':'No se pudo obtener la informacion'}
		return render(request, 'analyze/validation_error.html', context)
	#else ask riot for the last 20 games
	url = "https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/" + puuid  + "/ids?count=20"
	answer = requests.get(url, headers=utils.RIOT_HEADER)
	if(answer.status_code == 200):
		m_list = json.loads(answer.text)
		for match in m_list:
			try:
				Match.objects.get(match_id = match)
			except ObjectDoesNotExist:
				url2 = "https://europe.api.riotgames.com/tft/match/v1/matches/" + match
				answer2 = requests.get(url2, headers=utils.RIOT_HEADER)
				if(answer2.status_code == 200):
					m_info = json.loads(answer2.text)
					data = m_info["info"]
					part_list = data["participants"]
					for p in part_list:
						Match(match_id=match, puuid=p["puuid"], placement=p["placement"], level=p["level"]).save()
						part_units = p["units"]
						for u in part_units:
							items = u["items"]
							new_u = MatchUnit(match_id=match, puuid=p["puuid"], tier=u["tier"], unit=u["character_id"])
							new_u.save()
							for item_num in items:
								i = Item.objects.get(item_id=item_num)
								new_u.items.add(i)
							new_u.save()
						part_traits = p["traits"]
						for t in part_traits:
							MatchTrait(match_id=match, puuid=p["puuid"], tier=t["tier_current"], trait=t["name"], num_units=t["num_units"]).save()
			except MultipleObjectsReturned:
				pass
	url='/tft/user/' + user_name
	return redirect(url)

#/tft/user/{user_name}
def users(request, user_name):
	#haces get() en Summoners con ese user_name
	#si da exception hay mas de uno, delete() y buscas en la api incluido ranking
	#si da exception no hay ninguno, buscas en la api incluido ranking
	summ = None
	try:
		summ = Summoner.objects.get(name=user_name)
	except ObjectDoesNotExist:
		summ = ana.save_new_summ(user_name)

	except MultipleObjectsReturned:
		Summoner.objects.filter(name=user_name).delete()
		summ = ana.save_new_summ(user_name)

	if not summ:
		from userManagement.views import alreadyFavorited         
		context={'streams':getStreams(5), 'signup_form':SignupForm(), 'already_favorite':alreadyFavorited(request,summ)}
		return render(request,'analyze/users.html', context)

	
	#en este punto tienes un objeto summoner
	#con el puuid buscas en match
	match_set = Match.objects.filter(puuid=summ.puuid).order_by("-match_id")[:20]

	#en este punto tienes los matchids pero no las piezas y las sinergias
	#con el puuid y el matchid buscas en MatchTrait y MatchUnit la infomacion de cada partida
	matches = []
	for m in match_set:
		units = MatchUnit.objects.filter(puuid=summ.puuid, match_id=m.match_id)
		for u in units:
			u.unit = u.unit.replace('TFT3_', '').lower()
		aux = {}
		aux['info'] = m
		aux['units'] = units
		traits = MatchTrait.objects.filter(puuid=summ.puuid, match_id=m.match_id)
		aux['traits'] = traits
		matches.append(aux)

	#en este punto tienes toda la informacion y solo te falta hacer el analisis con PANDAS y los añadidos
	#filtras las últimas 20 partidas(por '-match_id'[:20])
	#analizas con PANDAS de forma similar a como lo haces en la vista units

	unit_sets = ana.analyze_user_units(matches)

	trait_sets = ana.analyze_user_traits(matches)

	object_sets = ana.analyze_user_objects(matches)

	image = ana.get_seaborn_histogram(matches)

	if(len(matches) > 5):
		matches = matches[:5]

	from userManagement.views import alreadyFavorited
	context={'image':image,'un_list':unit_sets,'trait_list':trait_sets,'object_list':object_sets,'streams':getStreams(5), 'signup_form':SignupForm(), 'summoner':summ, 'matches':matches, 'already_favorite':alreadyFavorited(request,summ)}
	return render(request,'analyze/users.html', context)

#/tft/traits/
def traits(request):
	trait_list = []
	controller = utils.Controller()
	controller.traits_lock.acquire()

	if( controller.traits_last_update < (datetime.now() - timedelta(seconds= 24 * 3600)) ):
		controller.update_traits_time()
		controller.traits_lock.release()
		#create my global index
		g_index = utils.get_traits_index()

		#create the DataFrame with that index
		df = DataFrame(index=g_index, dtype=np.int8)
		df_counter = 1

		#pick tops from my DB
		top_list = Top.objects.all()

		#for each top get its last 20 games
		#and create a Series for each game
		for t in top_list:
			try:
				s=Summoner.objects.get(name=t.name)
				raw_match_list=Match.objects.filter(puuid=s.puuid).order_by("-match_id")[:20]
				for m in raw_match_list:
					t_list = MatchTrait.objects.filter(puuid=s.puuid, match_id=m.match_id)
					serie = Series(index=g_index)
					for t in t_list:
						serie[t.trait] = m.placement
					df[df_counter] = serie
					df_counter = df_counter + 1
			except:
				pass

		trait_list = ana.analyze_full_dataframe(df, g_index)
		#update the database
		thread_DB = threading.Thread(target=db_comm.update_traits, args=(trait_list,))
		thread_DB.start()
	else:
		controller.traits_lock.release()
		aux_tr_list=AnalyzeTrait.objects.all()
		for trait in aux_tr_list:
			trait_list.append({
				"id" : trait.name.lower(),
				"name" : trait.name,
				"games" : trait.games,
				"mean" : trait.mean,
				"first" : trait.first,
				"top4" : trait.top,
				"losses" : trait.losses,
				})
	#build the context
	trait_list.sort(key=utils.sort_by_games)
	place =1
	for tr in trait_list:
		tr['place']= place
		place = place + 1
	#things needed by base.html
	signup_form=SignupForm()
	streams=getStreams(5)
	context={'trait_list':trait_list,'streams':streams, 'signup_form':signup_form}
	return render(request, 'analyze/traits.html', context)
	


#####/tft/objects/
def objects(request):
	object_list = []
	controller = utils.Controller()
	controller.objects_lock.acquire()

	if( controller.objects_last_update < (datetime.now() - timedelta(seconds= 24 * 3600)) ):
		controller.update_objects_time()
		controller.objects_lock.release()
		#create my global index
		g_index = utils.get_objects_index()

		#create the Series with that index
		serie = Series(index=g_index, dtype=np.int8)
		last20_serie = Series(index=g_index, dtype=np.int8)
		for name in g_index:
			serie[name] = 0
			last20_serie[name] = 0

		#pick tops from my DB
		top_list = Top.objects.all()

		#for each top get its last 20 games
		for t in top_list:
			try:
				s=Summoner.objects.get(name=t.name)
				raw_match_list=Match.objects.filter(puuid=s.puuid).order_by("-match_id")[:20]
				for m in raw_match_list:
					unit_list = MatchUnit.objects.filter(puuid=s.puuid, match_id=m.match_id)
					for u in unit_list:
						try:
							for o in u.items.all():
								serie[o.name] = serie[o.name] + 1
						except:
							pass
				if(len(raw_match_list) > 0):		
					last_match = raw_match_list[0]
					unit_list = MatchUnit.objects.filter(puuid=s.puuid, match_id=last_match.match_id)
					for u in unit_list:
							try:
								for o in u.items.all():
									last20_serie[o.name] = last20_serie[o.name] + 1
							except:
								pass

			except:
				pass

		for name in g_index:
			object_list.append({
				"id" : str(Item.objects.get(name=name).item_id).zfill(2),
				"name" : name,
				"games" : serie[name],
				"last_games" : last20_serie[name],
				})
		#update the database
		thread_DB = threading.Thread(target=db_comm.update_objects, args=(object_list,))
		thread_DB.start()
	else:
		controller.objects_lock.release()
		aux_object_list=AnalyzeObject.objects.all()
		for name in aux_object_list:
			object_list.append({
				"id" : str(Item.objects.get(name=name.name).item_id).zfill(2),
				"name" : name.name,
				"games" : name.games,
				"last_games" : name.last_games,
				})
	#build the context
	object_list.sort(key=utils.sort_by_games)
	place =1
	for name in object_list:
		name['place']= place
		place = place + 1
	#thing needed by base.html
	signup_form=SignupForm()
	streams=getStreams(5)
	context={'object_list':object_list,'streams':streams, 'signup_form':signup_form}
	return render(request, 'analyze/objects.html', context)










##### FUNCTIONS LISTENING TO AJAX REQUESTS #####

def ajax_top(request, count):
	count = int(count) + 20
	top_list=Top.objects.all().order_by('-league_points', 'name')[:count]
	#add extra informacion to display
	place = 1
	for s in top_list:
		s.winrate= float(s.wins * 100) / s.losses
		s.place = place
		place = place + 1
	response = '<tr><th scope="col">Rank</th><th scope="col">Name</th><th scope="col">Points</th><th scope="col">Wins</th><th scope="col">Losses</th><th scope="col">Winrate</th></tr></thead><tbody>'
	for t in top_list:
		response = response + '    <tr> <th scope="row">' + str(t.place)  + '</th>'
		response = response + '<td><a href= "../user/' + t.name  + '">' + t.name + '</a></td>'
		response = response + '<td>' + str(t.league_points) + '</td>'
		response = response + '<td>' + str(t.wins) + '</td>'
		response = response + '<td>' + str(t.losses) + '</td>'
		response = response + '<td>' + "{:.2f}".format(t.winrate) + '</td>'
		response = response +'</tr>'
	response = response + '</tbody></table>'
	return HttpResponse(response, status=200)
	
def ajax_twitch(request, stream_amount):
   new_stream_amount=int(stream_amount)+5
   streams=getStreams(stream_amount)
   response=""
   for stream in streams:
      response=response+'<div class="list-group-item list-group-item-action bg-light">'
      response=response+'<div class="d-flex justify-content-start flex-wrap flex-column">'
      response=response+'<a href="https://twitch.tv/'+stream[0]+' target="_blank">'
      response=response+'<img src="'+stream[2]+'" alt="'+stream[0]+'" height="100" width="178" class="p-2"></a>'
      response=response+'<a href="https://twitch.tv/'+stream[0]+'" target="_blank" class="align-self-baseline">'+stream[0]+'</a>'
      response=response+'<font size="-1">'+stream[1]+'</font></div></div>'
   response=response+'<button type="button" class="btn btn-secondary" onclick="ejecutarAJAX3('+str(new_stream_amount)+')">Cargar más</button>'     
   return HttpResponse(response, status=200)

def ajax_users(request, user_name):

	summ = Summoner.objects.get(name=user_name)	

	match_set = Match.objects.filter(puuid=summ.puuid).order_by("-match_id")[:20]

	#en este punto tienes los matchids pero no las piezas y las sinergias
	#con el puuid y el matchid buscas en MatchTrait y MatchUnit la infomacion de cada partida
	matches = []
	response = ''
	for m in match_set:
		response = response + '<li class="list-group-item"><div class="d-flex flex-row bd-highlight mb-3"><div class="p-2 bd-highlight">'
		response = response + '<h2>#' + str(m.placement) + '</h2>'
		response = response + '<p>Nivel: ' + str(m.level) + '</p>'
		response = response + '<p>fullGame: ' + m.match_id + '</p></div>'
		units = MatchUnit.objects.filter(puuid=summ.puuid, match_id=m.match_id)
		for u in units:
			u.unit = u.unit.replace('TFT3_', '').lower()
			response = response + '<div class="p-2 bd-highlight"><div class="card" style="width: 7rem;">'
			response = response + '<img src="' + "/static/analyze/images/units/" + u.unit + '.png" class="card-img-top" alt="' + u.unit + '">'
			response = response + '<div class="card-body"><svg class="bi bi-star-fill" style="font-size: 1em" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.283.95l-3.523 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/></svg>'
			if u.tier >= 2:
				response = response + '<svg class="bi bi-star-fill" style="font-size: 1em" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.283.95l-3.523 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/></svg>'
			if u.tier >= 3:
				response = response + '<svg class="bi bi-star-fill" style="font-size: 1em" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.283.95l-3.523 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/></svg>'
			response = response + '</div></div></div>'
		response = response + '</div></li>'

	return HttpResponse(response, status=200)

### Funcion que saca 5 videos sobre guias de una sinergia en Youtube
def getGuides(request,trait_name):
   parameters={"part": "id,snippet", "regionCode": "es", "maxResults": "3", "type": "video", "videoCategoryId": "20", "key": "YOUR-YOUTUBE-KEY-HERE", "q": "q=teamfight tactics guia "+trait_name}
   getguides_answer = requests.get("https://www.googleapis.com/youtube/v3/search",params=parameters)
   if (getguides_answer.status_code==200):
      json_answer = json.loads(getguides_answer.text)
      json_list = json_answer["items"]
      response = ''
      for entry in json_list:
         response = response + '<div> <div><img src=\"' + entry["snippet"]["thumbnails"]["default"]["url"] + '\"> </div> <div><a href=\"https://www.youtube.com/watch?v=' + entry["id"]["videoId"] + '\"</div><div>' + entry["snippet"]["title"]+ '</div> <div>' + entry["snippet"]["channelTitle"] + '</div></div>'
   else:
      response = '<div>No se pudieron recuperar los vídeos</div>'
   return HttpResponse(response, status=200)
