from django.db import models

class LAMStation(models.Model):
	lamid = models.IntegerField()
	name = models.CharField(max_length=99)
	lat = models.FloatField()
	lng = models.FloatField()

class LAMObs(models.Model):
	lamid = models.IntegerField()
	timestamp = models.IntegerField()
	trafficvol1 = models.IntegerField()
	trafficvol2 = models.IntegerField()
	avgspeed1 = models.IntegerField()
	avgspeed2 = models.IntegerField()

class LAMFcast(models.Model):
	lamid = models.IntegerField()
	timestamp = models.IntegerField()
	trafficvol1 = models.FloatField()