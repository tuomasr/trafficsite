import csv
from lam.models import LAMStation
from __future__ import unicode_literals

def main():
	with open('lam/lam_stations_small.csv','rb') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			d = LAMStation(lamid=int(row[0]),name=row[1],lat=float(row[2]),lng=float(row[3]))
			d.save()


main()