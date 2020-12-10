from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from analyze.models import Summoner

# Create your models here.
		
class Favorite(models.Model):
	user = models.ForeignKey(
           settings.AUTH_USER_MODEL,
           on_delete=models.CASCADE,
        )
	summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
	
	def __unicode__(self):
		return self.user
