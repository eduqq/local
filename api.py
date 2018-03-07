import numpy as np
import pandas as pd
import csv
from netCDF4 import Dataset
from flask import Flask, url_for, request, json, Response, jsonify, render_template


app = Flask(__name__)

# Importing the data:

# Marine13 MRA-free resulting from filter.py

df1 = pd.read_csv('filter.csv')

# R (MRA) from the model described in Butzin et al. (2017).
# temporal resolution = 50 yr.

fh = Dataset('MarineReservoirAge_0-15kcalBP_dt50years_0-100m.nc', mode = 'r')
lons = fh.variables['lon'][:]
lats = fh.variables['lat'][:]
time = fh.variables['time'][:]
MRAavgs = fh.variables['MRA_avg'][:, :, :]
fh.close

# Converting the longitude data in the original file to the range (-180, 180):

new_lons = [] 
for i in lons:
    new_lons.append(((i + 180 ) % 360) - 180)

new_lons = np.asarray(new_lons)

# This function finds the coordinates available in the model that are the closest to the study location:

def find_nearest(array,value):
    nearest = (np.abs(array-value)).argmin()
    return array[nearest]

# This function finds the index of the coordinates available in the model that are the closest to the study location.

def find_idx(array,value): 
    idx = (np.abs(array-value)).argmin()
    return idx

# resolution Marine13: 0-10500 (5), 10500-25000 (10), 25000-50000 (20).
# resolution Butzin et al. (2017) data: 0-50000 (50).
# This function interpolates model's data to match Marine13 MRA-free temporal resolution.
# It puts all sections of the interpolated MRA (same resolution of MRA-free Marine13) together. 

def interpolation(time, MRA):

    s1 = list(np.arange(0, 10501, 5))
    MRA_interp1 = list(np.interp(s1, time, MRA))
    s2 = list(np.arange(10510, 25001, 10))
    MRA_interp2 = list(np.interp(s2, time, MRA))
    s3 = list(np.arange(25020, 50001, 20))
    MRA_interp3 = list(np.interp(s3, time, MRA))

    s = (s1 + s2 + s3) 
    MRA_interp = (MRA_interp1 + MRA_interp2 + MRA_interp3)

    df2 = pd.DataFrame({'year':s, 'MRA_avg':MRA_interp})

    return df2

# This removes high frequency components of the MRA timeseries.
# The filter causes data loss at the beginning and at the end of the timeseries. This performs eflections at the extremes.
# The function builds the MRA timeseries and smoothes it.

def smooth_time_series(year, MRA_avg, year_end, MRA_avg_end, middle):

    

    year_r = np.asarray(list(reversed(year)))
    MRA_avg_r = np.asarray(list(reversed(MRA_avg)))
    year_end_r = np.asarray(list(reversed(year_end)))
    MRA_avg_end_r = np.asarray(list(reversed(MRA_avg_end)))

    begin_r = pd.DataFrame({'year': year_r, 'MRA_avg': MRA_avg_r}) 
    end_r = pd.DataFrame({'year': year_end_r, 'MRA_avg': MRA_avg_end_r}) 
    timeseries = pd.concat([begin_r, middle, end_r]) 

    timeseries['MRA_trend'] = timeseries['MRA_avg'].rolling(win_type = 'triang', window=201, center=True).mean()

    timeseries = timeseries[pd.notnull(timeseries['MRA_trend'])]

    return timeseries

# Returning the values: 
# Here the MRA timeseries is added together with the MRA-free Marine13 (same time resolution).
# The local curve is calculated and added to the combined dataframe which is exported to a .csv file.
# The local curve (specific columns of the df) is stored as json.

def create_http_response(df, lat, lon):
    
    out = df[['Radiocarbon Determination (BP)', 'year', 'error_Marine13_detrended']].to_json() 
    data = json.loads(out)

    latitude = str(lat)
    longitude = str(lon)

    keys = data['Radiocarbon Determination (BP)'].keys() 
    keys.sort(key=float)
    return Response(render_template('test.html', result={'keys':keys, 'data':data, 'Details':{'Place': 'Sea'}, 'Valid': 'True',\
        'Latitude': latitude, 'Longitude': longitude}))

# Returning data for the closest available region when user chooses an invalid location:
# Here the MRA timeseries is added together with the MRA-free Marine13 (same time resolution).
# The local curve is calculated and added to the combined dataframe which is exported to a .csv file.
# The local curve (specific columns of the df) is stored as json.

def invalid_location(df, lat, lon):
    
    out = df[['Radiocarbon Determination (BP)', 'year', 'error_Marine13_detrended']].to_json() 
    data = json.loads(out)

    latitude = str(lat)
    longitude = str(lon)

    keys = data['Radiocarbon Determination (BP)'].keys() 
    keys.sort(key=float)
    return Response(render_template('test.html', result={'keys':keys, 'data':data, 'Details':{'Place': 'Sea'}, 'Valid': 'False', \
        'Latitude': latitude, 'Longitude': longitude}))
            
# Returning error message (e.g., incorrect URLs):
    
@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

# Getting data for a chosen location (inputing latitude and longitude):
# URL in the format http://127.0.0.1:5000/coordinates?lon=0&lat=0.

@app.route('/coordinates', methods = ['GET'])
def function1():

    lon = float(request.args.get('lon')) 
    lat = float(request.args.get('lat'))

    if lon in new_lons and lat in lats: 
        
        lat_idx = find_idx(lats, lat)
        lon_idx = find_idx(new_lons, lon)
        MRA = MRAavgs [:, lat_idx, lon_idx] 

        interp = interpolation(time, MRA)
        timeseries = smooth_time_series(interp['year'][0:100], interp['MRA_avg'][0:100], interp['year'][4701:4801].reset_index(drop=True), interp['MRA_avg'][4701:4801].reset_index(drop=True), interp)
        
        if np.ma.is_masked(MRA):
            message = {
            'Valid': False, 'Details': {'Place': 'Land'} 
            }
            resp = jsonify(message)
            return resp
        
        else:
			df = df1.join(timeseries)
			df['Radiocarbon Determination (BP)'] = df['Marine13_detrended'] + df['MRA_trend']
			df.to_csv('LOCal13.csv', index=False, header=True)
			return create_http_response(df, lat, lon)
            
    elif lon not in new_lons or lat not in lats:
        
        lon = find_nearest(new_lons, lon)
        lat = find_nearest(lats, lat)
	lat_idx = find_idx(lats, lat)
        lon_idx = find_idx(new_lons, lon)
        MRA = MRAavgs [:, lat_idx, lon_idx] 

        interp = interpolation(time, MRA)
        timeseries = smooth_time_series(interp['year'][0:100], interp['MRA_avg'][0:100], interp['year'][4701:4801].reset_index(drop=True), interp['MRA_avg'][4701:4801].reset_index(drop=True), interp)


        if np.ma.is_masked(MRA):
            message = {
            'Valid': False, 'Details': {'Place': 'Land'} 
            }
            resp = jsonify(message)
            return resp

        else:
			df = df1.join(timeseries)
			df['Radiocarbon Determination (BP)'] = df['Marine13_detrended'] + df['MRA_trend']
			df.to_csv('LOCal13.csv', index=False, header=True)
			return invalid_location(df, lat, lon)

    
if __name__ == '__main__':
    app.run()









   

