import json

import math


from analyze.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from pandas import DataFrame, Series
import pandas
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import urllib
import requests

import analyze.utils as util


####GET INFO FROM RIOT API FUNCTIONS####

#get last 5 games for new users

def get_user_games(puuid):
	url = "https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/" + puuid  + "/ids?count=5"
	answer = requests.get(url, headers=util.RIOT_HEADER)
	if(answer.status_code == 200):
		m_list = json.loads(answer.text)
		for match in m_list:
			try:
				Match.objects.get(match_id = match)
			except ObjectDoesNotExist:
				url2 = "https://europe.api.riotgames.com/tft/match/v1/matches/" + match
				answer2 = requests.get(url2, headers=util.RIOT_HEADER)
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

#get a user and store it in DB

def save_new_summ(user_name):
	summ = None
	answer_summ = requests.get('https://euw1.api.riotgames.com/tft/summoner/v1/summoners/by-name/' + user_name, headers=util.RIOT_HEADER)
	if (answer_summ.status_code == 200):
		json_summ = json.loads(answer_summ.text)
		answer_league = requests.get('https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + json_summ["id"], headers=util.RIOT_HEADER)
		if (answer_league.status_code == 200):
			json_leagues = json.loads(answer_league.text)

			json_league = None
			for league in json_leagues:
				if (league['queueType'] == "RANKED_TFT"):
					json_league = league

			if not json_league:
				summ = Summoner(puuid = json_summ['puuid'], name = json_summ['name'], summoner_id = json_summ['id'], 
					account_id = json_summ['accountId'], summoner_level = json_summ['summonerLevel'], tier = 'UNRANKED', 
					rank = '0', league_points = '0', wins = 0, losses = 0, top_4 = 0, profile_pic=json_summ['profileIconId'])
				summ.save()
			else:
				summ = Summoner(puuid = json_summ['puuid'], name = json_summ['name'], summoner_id = json_summ['id'], 
					account_id = json_summ['accountId'], summoner_level = json_summ['summonerLevel'], tier = json_league['tier'], 
					rank = json_league['rank'], league_points = json_league['leaguePoints'], wins = json_league['wins'], losses = json_league['losses'], top_4 = 0, profile_pic=json_summ['profileIconId'])
				summ.save()
			get_user_games(summ.puuid)
	return summ



####ANALYZE USER INFO####

def analyze_full_dataframe(df, g_index):
	return_list = []

	count_serie = df.count(axis='columns')#get games played

	mean_serie = df.mean(axis=1, skipna=True)#get mean possition 

	df2 = df.transpose()
	
	#get victories and top4
	for un in g_index:
		u_serie = df2[un].value_counts()
		first = 0
		try:
			first = u_serie[1]
		except:
			pass
		second = 0
		try:
			second = u_serie[2]
		except:
			pass
		third = 0
		try:
			third = u_serie[3]
		except:
			pass
		forth = 0
		try:
			forth = u_serie[4]
		except:
			pass
		top4 = first + second + third + forth
		if math.isnan(mean_serie[un]):
			mean_serie[un]=0
		return_list.append({
			"id" : un.replace('TFT3_','').replace('Set3_','').lower(),
			"name" : un.replace('TFT3_','').replace('Set3_',''),
			"games" : count_serie[un],
			"mean" : mean_serie[un],
			"first" : first,
			"top4" : top4,
			"losses" : count_serie[un] - first,
			})

	return return_list


#analize units

def analyze_user_units(matches):
	un_list = []
	
	f_index = util.get_units_index()
	g_index = []
	for u in f_index:
		g_index.append(u.replace('TFT3_','').lower())


	#create the DataFrame with that index
	df = DataFrame(index=g_index, dtype=np.int8)
	df_counter = 1


	for m in matches:
		unit_list = m['units']
		serie = Series(index=g_index)
		for u in unit_list:
			serie[u.unit] = m['info'].placement
		df[df_counter] = serie
		df_counter = df_counter + 1

	un_list = analyze_full_dataframe(df, g_index)

	#build the context
	un_list.sort(key=util.sort_by_games)
	place =1
	for un in un_list:
		un['place']= place
		place = place + 1


	return un_list[:5]

#analyze traits

def analyze_user_traits(matches):
	trait_list = []
	g_index = util.get_traits_index()
	df = DataFrame(index=g_index, dtype=np.int8)
	df_counter = 1
	
	for m in matches:
		t_list = m['traits']
		serie = Series(index=g_index)
		for t in t_list:
			serie[t.trait] = m['info'].placement
		df[df_counter] = serie
		df_counter = df_counter + 1

	trait_list = analyze_full_dataframe(df, g_index)

	trait_list.sort(key=util.sort_by_games)
	place =1
	for tr in trait_list:
		tr['place']= place
		place = place + 1
	return trait_list[:5]

#analyze objects

def analyze_user_objects(matches):
	object_list = []
	g_index = util.get_objects_index()

	#create the Serie with that index
	serie = Series(index=g_index, dtype=np.int8)
	for name in g_index:
		serie[name] = 0


	for m in matches:
		unit_list = m['units']
		for u in unit_list:
			try:
				for o in u.items.all():
					serie[o.name] = serie[o.name] + 1
			except:
				pass

	for name in g_index:
		num = Item.objects.get(name=name).item_id
		my_id = str(num)
		if (num < 10):
			my_id = '0' + my_id
		object_list.append({
			"name" : name,
			"id" : my_id,
			"games" : serie[name],
			})

	#build the context
	object_list.sort(key=util.sort_by_games)
	place =1
	for name in object_list:
		name['place']= place
		place = place + 1
	
	return object_list[:5]



####GENERATE SEABORN FIGURES####

#seaborn histogram

def get_seaborn_histogram(matches):
	#generate info to plot
	g_index = []
	for m in matches:
		g_index.append(m['info'].match_id)
	serie = Series(index=g_index, dtype=np.int8)
	for m in matches:
		serie[m['info'].match_id] = m['info'].placement
	df = DataFrame(index=g_index, dtype=np.int8)
	df['placement'] = serie
	sns.countplot(x ='placement', data = df)

	#change image to byte array and encode as base64
	figure = plt.gcf()
	FigureCanvasAgg(figure)
	buf = io.BytesIO()
	figure.savefig(buf, format='png', transparent=True, quality=100, dpi=200)
	buf.seek(0)
	imsrc = base64.b64encode(buf.read())
	imuri = 'data:image/png;base64,{}'.format(urllib.parse.quote(imsrc))

	#clean for the next plot
	plt.close()

	return imuri
