from celery.task.schedules import crontab
from celery.decorators import periodic_task
from .models import LAMStation, LAMObs, LAMFcast

import xmltodict
import urllib2
from datetime import datetime
import time
from django_pandas.io import read_frame
import pandas as pd
import numpy as np
import GPy
from matplotlib import pyplot as pb

def read_xml(url):
	file = urllib2.urlopen(url)
	xml = file.read()
	file.close()

	# parse the XML data
	return xmltodict.parse(xml)

def plot2(m,Xnew,Ynew):
	fig = pb.figure(figsize=(12,8))
	ax1 = pb.subplot(111)
	ax1.set_title('Output 1')
	m.plot(ax=ax1)
	ax1.plot(Xnew,Ynew,'gx',mew=1.5)

@periodic_task(run_every=(crontab(minute='*/5')), name="fetch_lam_data", ignore_result=True)
def data_fetch():
	# specify URLs
	url = 'http://tie.digitraffic.fi/sujuvuus/ws/lamData'

	try:
		doc = read_xml(url)
		working = 1
	except:
		working = 0

	# loop links
	if working:
		print 'reading lam data...'

		# loop lams
		for item in doc['soap:Envelope']['soap:Body']['LamDataResponse']['lamdynamicdata']['lamdata']:
			# read lamid
			lamid = item['lamid']

			# parse a UTC datetime and convert it into unix time
			dt = datetime.strptime(item['measurementtime']['utc'][:-1],'%Y-%m-%dT%H:%M:%S')
			et = str(int((dt - datetime(1970,1,1)).total_seconds()))

			# read traffic volumes and speeds
			tv1 = item['trafficvolume1']
			tv2 = item['trafficvolume2']
			avgs1 = item['averagespeed1']
			avgs2 = item['averagespeed2']

			d = LAMObs(lamid=lamid, timestamp=et, trafficvol1=tv1, trafficvol2=tv2, avgspeed1=avgs1, avgspeed2=avgs2)
			d.save()
	else:
		print 'something failed when reading the xml.'
	
	# wait until updating data again
	print 'sleeping 300 secs.'

#@periodic_task(run_every=(crontab()), name="update_fcast", ignore_result=True)
@periodic_task(run_every=(crontab(minute=0, hour='*/1')), name="update_fcast", ignore_result=True)
def update_fcast():
	# get the lamstations ordered by their id
	qs = LAMStation.objects.order_by('lamid')


	# train a model for each station
	for lam_station in qs:
		lamid = lam_station.lamid
		#ms = int(datetime.now().strftime("%s")) * 1000 

		# fetch data for this station
		obs = LAMObs.objects.filter(lamid=lamid)

		if obs is None:
			break
		else:
			obs = obs.order_by('timestamp')[obs.count()-1000:]

		data = read_frame(obs)

		# obtain input and output vectors for modelling
		X = np.atleast_2d(data['timestamp'].values).T
		Y = np.atleast_2d(data['trafficvol1'].values).T

		# standardize data
		Xmean = np.mean(X)
		Xstd = np.std(X)
		Xmax = np.max(X)
		Xend = Xmax+1000*60
		Ymean = np.mean(Y)
		Ystd = np.std(Y)

		if Xstd == 0 or Ystd == 0:
			break

		X = (X-Xmean) / Xstd
		Xmax = (Xmax-Xmean) / Xstd
		Xend = (Xend-Xmean) / Xstd
		Y = (Y-Ymean) / Ystd

		# specify the kernel
		k1 = GPy.kern.RBF(1)
		#k2 = GPy.kern.PeriodicExponential(1)
		kernel = k1

		# setup the model
		try:
			m = GPy.models.GPRegression(X,Y,kernel)
		except:
			break

		# optimize hyperparameters
		m.optimize_restarts(num_restarts = 2)

		Xnew = np.linspace(Xmax,Xend,20)
		Xnew = np.atleast_2d(Xnew).T
		Ynew = m.predict(Xnew)

		# make input and output absolute again
		Xnew = Xnew*Xstd+Xmean
		Ynew = Ynew*Ystd+Ymean

		for i in range(0,Xnew.size):
			d = LAMFcast(lamid=lamid,timestamp=Xnew[i],trafficvol1=Ynew[0][i])
			d.save()