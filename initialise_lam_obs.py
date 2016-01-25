import csv
import glob
from lam.models import LAMStation, LAMObs

def main():
	qs = LAMStation.objects.all()
	lamid_accept = [q.lamid for q in qs]
	print lamid_accept
	files = glob.glob('lam/lamobs/*')
	for f in files:
		lamid = f.replace("lam/lamobs/lam","")
		if int(lamid) in lamid_accept:
			with open(f) as ff:
				lines = ff.readlines()
				j = 0
				for line in lines:
					if (j > 19000):
						row = line.split(',')
						d = LAMObs(lamid=int(lamid),timestamp=row[0],trafficvol1=row[1],trafficvol2=row[2],avgspeed1=row[3],avgspeed2=row[4])
						d.save()
					
					j = j + 1

main()