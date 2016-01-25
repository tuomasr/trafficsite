from django.template import Context, RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from lam.models import LAMStation, LAMObs, LAMFcast
from django_pandas.io import read_frame
from django.core import serializers
from django.db.models import Func, F
from django.db.models import Avg, Max, Min
import json

def compute_color(tv,tv_min,tv_max):
	# linear color changes
	tv_index = float(tv-tv_min)/(tv_max-tv_min)
	tv_index = max(0, min(tv_index,1))

	if (tv_index <= 0.5):
		r = 255*tv_index/0.5
		g = 255
		b = 0
	else:
		r = 255
		g = 255-255*(tv_index-0.5)/0.5
		b = 0

	return '#%02x%02x%02x' % (r, g, b)

def update_colors(ts, tp):
	# initialise the returned dict
	data = {}

	# get the lamstations ordered by their id
	qs = LAMStation.objects.order_by('lamid')
	j = 0

	for lam_station in qs:
		lamid = lam_station.lamid

		# fetch data from the database corresponding to this timestamp
		obs = LAMObs.objects.filter(lamid=lamid)
		tv_min = obs.aggregate(Min('trafficvol1'))
		tv_max = obs.aggregate(Max('trafficvol1'))
		tv_min = tv_min['trafficvol1__min']
		tv_max = tv_max['trafficvol1__max']

		if tp == 'obs':
			obs = obs.filter(timestamp__lte=ts).order_by('-timestamp').first()
		elif tp == 'fcast':
			obs = LAMFcast.objects.filter(lamid=lamid).filter(timestamp__lte=ts).order_by('-timestamp').first()

		if obs is not None and tv_max > 0 and tv_min > 0 and not tv_min==tv_max:
			print "success."
			data[j] = compute_color(obs.trafficvol1,tv_min,tv_max)
		else:
			print "fail."
			data[j] = "#FFFF00"
		j = j + 1

	return data

def index(request):
	# send lamstations to the map in ascending order with respect to their lamid
	qs = LAMStation.objects.order_by('lamid');
	lam_stations = serializers.serialize("json", qs)
	
	return render_to_response('index.html', RequestContext(request, {"lam_stations":lam_stations}))

def update_map(request):
	if request.method == 'POST':
		# get the timestamp in UTC
		ts = request.POST.get('timestamp')
		tp =  request.POST.get('type')
		
		response_data = update_colors(ts, tp)

		return HttpResponse(json.dumps(response_data),content_type="application/json")