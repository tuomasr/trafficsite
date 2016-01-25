# trafficsite
Visualise historical, current and future traffic on a map of the Helsinki region. Employ multi-output Gaussian process regression to make reliable predictions regardless of missing data.

# Data
The website uses "LAM" station data from the Finnish Transport Agency. Data is updated every 5 minutes. Please consult https://github.com/finnishtransportagency/digitraffic/wiki

# Dependencies
The website runs on Django and Google Maps API. Scheduled data fetches and model training is implemented with Celery and Redis. The Gaussian process regression model for predicting traffic volumes requires GPy. In addition, one must install
```
xmltodict
urllib2
pandas
django_pandas
numpy
```

# An example of the model
Multi-output Gaussian process regression seems to model the data relatively well. The model is excellent at adopting to situations where data is missing for some stations because the model can learn correlations between nearby stations. Below, I have simulated a missing data situation with the blue line being the mean prediction and the light blue area the confidence interval
![Example](example.png?raw=true "Example")
If the figure is not rendered, see example.png or run example_2d.py.

# TODO
Optimize user's route back home using current traffic information and predictions of possible traffic jams. 
