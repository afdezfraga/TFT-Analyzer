from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class Unit(models.Model):
	unit_id = models.CharField(max_length = 32, primary_key = True)
	name = models.CharField(max_length = 32)
	rarity = models.PositiveSmallIntegerField()
	trait1 = models.CharField(max_length = 32)
	trait2 = models.CharField(max_length = 32)
	trait3 = models.CharField(max_length = 32, blank=True)
	#image = models.se_explica_en_el_tutorial_3()

	def __unicode__(self):
		return self.unit_id


class Item(models.Model):
	item_id = models.PositiveSmallIntegerField(primary_key = True)
	name = models.CharField(max_length = 32)
	#image = models.se_explica_en_el_tutorial_3()

	def __unicode__(self):
		return self.name


class Trait(models.Model):
	trait_id = models.CharField(max_length = 32, primary_key = True)
	name = models.CharField(max_length = 32)
	bronce_min = models.PositiveSmallIntegerField(null=True)
	silver_min = models.PositiveSmallIntegerField(null=True)
	gold_min = models.PositiveSmallIntegerField(null=True)
	chromatic_min = models.PositiveSmallIntegerField(null=True)
	#image = models.se_explica_en_el_tutorial_3()

	def __unicode__(self):
		return self.trait_id

class Summoner(models.Model):
	#From SummonerDTO
	puuid = models.CharField(max_length = 79, primary_key = True)
	name = models.CharField(max_length = 64)
	summoner_id = models.CharField(max_length = 64)
	account_id = models.CharField(max_length = 57)
	summoner_level = models.PositiveIntegerField()
	#From LeagueEntryDTO
	tier = models.CharField(max_length = 32)
	rank = models.CharField(max_length = 32)
	league_points = models.PositiveSmallIntegerField()
	wins = models.PositiveIntegerField()
	losses = models.PositiveIntegerField()
	#From matches analisis
	top_4 = models.PositiveIntegerField()
	profile_pic = models.PositiveIntegerField()
	#image = models.se_explica_en_el_tutorial_3()

	def __unicode__(self):
		return self.name

class Match(models.Model):
	match_id = models.CharField(max_length = 255)
	puuid = models.CharField(max_length = 79)
	level = models.PositiveSmallIntegerField()
	placement = models.PositiveSmallIntegerField()

	def __unicode__(self):
		return self.match_id

class MatchTrait(models.Model):
	puuid = models.CharField(max_length = 79)
	match_id = models.CharField(max_length = 255)
	#trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
	trait = models.CharField(max_length = 32)
	tier = models.PositiveSmallIntegerField()
	num_units = models.PositiveSmallIntegerField()

	def __unicode__(self):
		return self.trait

class MatchUnit(models.Model):
	puuid = models.CharField(max_length = 79)
	match_id = models.CharField(max_length = 255)
	#unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
	unit = models.CharField(max_length = 32)
	tier = models.PositiveSmallIntegerField()
	items = models.ManyToManyField(Item)

	def __unicode__(self):
		return self.unit

class Top(models.Model):
	name = models.CharField(max_length = 64)
	summoner_id = models.CharField(max_length = 64)
	league_points = models.PositiveSmallIntegerField()
	wins = models.PositiveIntegerField()
	losses = models.PositiveIntegerField()

	def __unicode__(self):
		return self.name

class AnalyzeUnit(models.Model):
	#NO DESCOMENTAR AUN unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
	name = models.CharField(max_length = 32)
	games = models.PositiveIntegerField()
	mean = models.FloatField()
	first = models.PositiveIntegerField()
	top = models.PositiveIntegerField()
	losses = models.PositiveIntegerField()

	def __unicode__(self):
		return self.name
		
class AnalyzeTrait(models.Model):
	#NO DESCOMENTAR AUN trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
	name = models.CharField(max_length = 32)
	games = models.PositiveIntegerField()
	mean = models.FloatField()
	first = models.PositiveIntegerField()
	top = models.PositiveIntegerField()
	losses = models.PositiveIntegerField()

	def __unicode__(self):
		return self.name	

class AnalyzeObject(models.Model):
	#NO DESCOMENTAR AUN trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
	name = models.CharField(max_length = 32)
	games = models.PositiveIntegerField()
	last_games = models.PositiveIntegerField()

	def __unicode__(self):
		return self.name	
		
