import json

from analyze.models import *


def update_Top(json_list):
	Top.objects.all().delete()
	for summ in json_list:
		tmp = Top(summoner_id=summ["summonerId"], name=summ["summonerName"], league_points=summ["leaguePoints"], wins=summ["wins"], losses=summ["losses"])
		tmp.save()

def update_units(un_list):
	AnalyzeUnit.objects.all().delete()
	for summ in un_list:
		tmp = AnalyzeUnit(name=summ["name"], games=summ["games"], mean=summ["mean"], first=summ["first"], top=summ["top4"], losses=summ["losses"])
		tmp.save()

def update_traits(trait_list):
	AnalyzeTrait.objects.all().delete()
	for trait in trait_list:
		tmp = AnalyzeTrait(name=trait["name"], games=trait["games"], mean=trait["mean"], first=trait["first"], top=trait["top4"], losses=trait["losses"])
		tmp.save()

def update_objects(object_list):
	AnalyzeObject.objects.all().delete()
	for name in object_list:
		tmp = AnalyzeObject(name=name["name"], games=name["games"], last_games=name["last_games"])
		tmp.save()