import json

import math
from threading import Lock
import threading
from datetime import datetime, timedelta


from analyze.models import *


RIOT_HEADER = {"X-Riot-Token": "Your-Token-Goes-Here"}

####Contoller to update copy of analisis periodically and not on each request

class Controller:
	class __Controller:
		def __init__(self):
			self.top_lock = Lock()
			self.top_last_update = datetime.now() - timedelta(seconds= 5 * 60)

			self.units_lock = Lock()
			self.units_last_update = datetime.now() - timedelta(seconds= 24 * 3600)

			self.traits_lock = Lock()
			self.traits_last_update = datetime.now() - timedelta(seconds= 24 * 3600)

			self.objects_lock = Lock()
			self.objects_last_update = datetime.now() - timedelta(seconds= 24 * 3600)

		def update_top_time(self):
			self.top_last_update = datetime.now()

		def update_units_time(self):
			self.units_last_update = datetime.now()

		def update_traits_time(self):
			self.traits_last_update = datetime.now()

		def update_objects_time(self):
			self.objects_last_update = datetime.now()

	instance = None

	def __init__(self):
		if not Controller.instance:
			Controller.instance = Controller.__Controller()

	def __getattr__(self, name):
		return getattr(self.instance, name)


#### Sorting utilities

def sort_tops(s):
	return -s.league_points

def sort_by_games(u):
	return -u['games']

#### Get index utilities

def get_units_index():
	index = []
	for u in Unit.objects.all():
		index.append(u.unit_id)
	return index

def get_traits_index():
	index = []
	for t in Trait.objects.all():
		index.append(t.trait_id)
	return index

def get_objects_index():
	index = []
	for item in Item.objects.all():
		index.append(item.name)
	return index
