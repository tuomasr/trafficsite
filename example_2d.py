import numpy as np
import pandas as pd
import GPy
from matplotlib import pyplot as pb
import datetime

def plot_2outputs(m,X1,X2,Y1,Y2,Xmissing,Ymissing):
	slices = GPy.util.multioutput.get_slices([Y1,Y2])
	fig = pb.figure(figsize=(12,8))
	#Output 1
	ax1 = fig.add_subplot(211)
	ax1.set_title('Output 1')
	m.plot(fixed_inputs=[(1,0)],which_data_rows=slices[0],ax=ax1)
	ax1.plot(X1,Y1,'rx',mew=1.5,label='Keha 1 observed')
	ax1.legend()
	#Output 2
	ax2 = fig.add_subplot(212)
	ax2.set_title('Output 2')
	m.plot(fixed_inputs=[(1,0)],which_data_rows=slices[1],ax=ax2)
	ax2.plot(X2,Y2,'rx',mew=1.5,label='Keilaniemi observed')
	ax2.plot(Xmissing,Ymissing,'gx',mew=1.5,label='Keilaniemi missing')
	ax2.legend()
	

def main():
	# read data
	data1 = pd.read_table('lam/lam116',sep=',',header=None,names=['timestamp','trafficvolume1','trafficvolume2','averagespeed1','averagespeed2'],index_col=False)
	data2 = pd.read_table('lam/lam118',sep=',',header=None,names=['timestamp','trafficvolume1','trafficvolume2','averagespeed1','averagespeed2'],index_col=False)

	# convert utc timestamps to datetime
	data1['timestamp'] = data1['timestamp'].apply(datetime.datetime.utcfromtimestamp)
	data2['timestamp'] = data2['timestamp'].apply(datetime.datetime.utcfromtimestamp)
	data1 = data1.set_index('timestamp')
	data2 = data2.set_index('timestamp')

	# get average hourly values by resampling
	data1 = data1.resample('H')
	data2 = data2.resample('H')
	data1.dropna(inplace=True)
	data2.dropna(inplace=True)

	# remove outliers
	#data = data[data.averagespeed2 > 50]

	# obtain input and output vectors for modelling
	X1 = np.atleast_2d(data1.index.astype(np.int64) // 10**9).T
	X2 = np.atleast_2d(data2.index.astype(np.int64) // 10**9).T
	Y1 = np.atleast_2d(data1['trafficvolume1'].values).T
	Y2 = np.atleast_2d(data2['trafficvolume1'].values).T

	# standardize data
	X1 = (X1-np.mean(X1)) / np.std(X1)
	X2 = (X2-np.mean(X2)) / np.std(X2)
	Y1 = (Y1-np.mean(Y1)) / np.std(Y1)
	Y2 = (Y2-np.mean(Y2)) / np.std(Y2)

	offset = 60
	Xmissing = X2[(len(X2)-offset+1):len(X2)]
	Ymissing = Y2[(len(Y2)-offset+1):len(Y2)]
	X2 = X2[1:(len(X2)-offset)]
	Y2 = Y2[1:(len(Y2)-offset)]

	# specify the kernel
	k1 = GPy.kern.RBF(1)
	k2 = GPy.kern.PeriodicExponential(1)
	lcm = GPy.util.multioutput.LCM(input_dim=1,num_outputs=2,kernels_list=[k1,k2])

	# setup the model
	m = GPy.models.GPCoregionalizedRegression([X1,X2],[Y1,Y2],kernel=lcm)

	# optimize hyperparameters
	m.optimize_restarts(num_restarts = 20)

	# print model details
	print m

	# plot predictions
	plot_2outputs(m,X1,X2,Y1,Y2,Xmissing,Ymissing)
	
	pb.show()

main()