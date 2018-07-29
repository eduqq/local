import numpy as np
import pandas as pd
import csv
from netCDF4 import Dataset
from flask import Flask, url_for, request, json, Response, jsonify, render_template


app = Flask(__name__)

# Importing the data:

# IntCal13 and Marine13 (Delta14C and CRA).

df1 = pd.read_csv('Intcal13.csv')
df2 = pd.read_csv('Marine13.csv')

# MRA from the model described in Butzin et al. (2017).
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

# This function finds the coordinates available in the model that are the closest to the chosen location:

def find_nearest(array,value):
    nearest = (np.abs(array-value)).argmin()
    return array[nearest]

# This function finds the index of the coordinates available in the model that are the closest to the chosen location.

def find_idx(array,value): 
    idx = (np.abs(array-value)).argmin()
    return idx

# resolution Marine13: 0-10500 (5), 10500-25000 (10), 25000-50000 (20).
# resolution Butzin et al. (2017) data: 0-50000 (50).
# This function interpolates the model data to match the Marine13 temporal resolution.
# It puts all sections of the interpolated MRA (same resolution of Marine13) together. 

def interpolation(time, MRA):

    s1 = list(np.arange(0, 10501, 5))
    MRA_interp1 = list(np.interp(s1, time, MRA))
    s2 = list(np.arange(10510, 25001, 10))
    MRA_interp2 = list(np.interp(s2, time, MRA))
    s3 = list(np.arange(25020, 50001, 20))
    MRA_interp3 = list(np.interp(s3, time, MRA))

    s = (s1 + s2 + s3) 
    MRA_interp = (MRA_interp1 + MRA_interp2 + MRA_interp3)

    df3 = pd.DataFrame({'year':s, 'MRA_avg':MRA_interp})

    return df3

# This function removes high frequency components from the MRA timeseries.
# The filter causes data loss at the beginning and at the end of the timeseries. This function performs reflections at the extremes.
# The function builds the MRA timeseries and smoothes it.

def smooth_timeseries(year, cra, year_end, cra_end, error, error_end, middle):

    year_r = np.asarray(list(reversed(year)))
    cra_r = np.asarray(list(reversed(cra)))
    error_r = np.asarray(list(reversed(error)))
    year_end_r = np.asarray(list(reversed(year_end)))
    cra_end_r = np.asarray(list(reversed(cra_end)))
    error_end_r = np.asarray(list(reversed(error_end)))

    begin_r = pd.DataFrame({'year': year_r, 'cra': cra_r, 'error':error_r}) 
    end_r = pd.DataFrame({'year': year_end_r, 'cra': cra_end_r, 'error':error_end_r}) 
    smooth = pd.concat([begin_r, middle, end_r]) 

    smooth['cra_trend'] = smooth['cra'].rolling(win_type = 'triang', window=21, center=True).mean()
    smooth['error_trend'] = smooth['error'].rolling(win_type = 'triang', window=21, center=True).mean()

    smooth = smooth[pd.notnull(smooth['cra_trend'])]

    return smooth

# Returning the values: 
# The local curve is exported to a .csv file.
# The local curve is stored as json.

def create_http_response(df, lat, lon):
    
    out = df[['MRA_avg', 'year', 'Delta14C', 'Delta_sigma','Fm', 'cra_trend', 'error_trend']].to_json() 
    data = json.loads(out)

    latitude = str(lat)
    longitude = str(lon)

    keys = data['MRA_avg'].keys() 
    keys.sort(key=float)
    return Response(render_template('test.html', result={'keys':keys, 'data':data, 'Details':{'Place': 'Sea'}, 'Valid': 'True',\
        'Latitude': latitude, 'Longitude': longitude}))

# Returning data for the closest available region when user chooses an invalid location:
# The local curve is exported to a .csv file.
# The local curve is stored as json.

def invalid_location(df, lat, lon):
    
    out = df[['MRA_avg', 'year', 'Delta14C', 'Delta_sigma', 'Fm', 'cra_trend', 'error_trend']].to_json()
    data = json.loads(out)

    latitude = str(lat)
    longitude = str(lon)

    keys = data['MRA_avg'].keys() 
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
# CRA are calculated from IntCal13 and Butzin Data.

@app.route('/coordinates', methods = ['GET'])
def function1():

    lon = float(request.args.get('lon')) 
    lat = float(request.args.get('lat'))

    if lon in new_lons and lat in lats: 
        
        lat_idx = find_idx(lats, lat)
        lon_idx = find_idx(new_lons, lon)
        MRA = MRAavgs [:, lat_idx, lon_idx] 

        interp = interpolation(time, MRA)
        
        if np.ma.is_masked(MRA):
            message = {
            'Valid': False, 'Details': {'Place': 'Invalid'} 
            }
            resp = jsonify(message)
            return resp
        
        else:
			df = pd.DataFrame(interp)
        for row in df.iterrows():
                df['Delta14C'] = (df1['Delta14C_t']+1000)/(np.exp(df['MRA_avg']/8033))-1000
                df['Delta_sigma'] = df1['sigma']
                df['Fm'] = (df['Delta14C']/1000+1)*np.exp(df1['ad']/8033-0.24274866)
                df['cra'] = -(8033*np.log(df['Fm']))
                df['error'] = df2['error']
                df_smooth = smooth_timeseries(df['year'][0:10], df['cra'][0:10], df['year'][4791:4801].reset_index(drop=True), \
                    df['cra'][4791:4801].reset_index(drop=True), df['error'][0:10], df['error'][4791:4801].reset_index(drop=True), df)
		#df_smooth.to_csv('LOCal13_' + 'lat=' + str(lat) + 'lon=' + str(lon) + '.csv', index=False, header=True)
		return create_http_response(df_smooth, lat, lon)
            
    elif lon not in new_lons or lat not in lats:
        
        lon = find_nearest(new_lons, lon)
        lat = find_nearest(lats, lat)
	lat_idx = find_idx(lats, lat)
        lon_idx = find_idx(new_lons, lon)
        MRA = MRAavgs [:, lat_idx, lon_idx] 

        interp = interpolation(time, MRA)

        if np.ma.is_masked(MRA):
            message = {
            'Valid': False, 'Details': {'Place': 'Invalid'} 
            }
            resp = jsonify(message)
            return resp

        else:
			df = pd.DataFrame(interp)
        for row in df.iterrows():
                df['Delta14C'] = (df1['Delta14C_t']+1000)/(np.exp(df['MRA_avg']/8033))-1000
                df['Delta_sigma'] = df1['sigma']
                df['Fm'] = (df['Delta14C']/1000+1)*np.exp(df1['ad']/8033-0.24274866)
                df['cra'] = -8033*np.log(df['Fm'])
                df['error'] = df2['error']
                df_smooth = smooth_timeseries(df['year'][0:10], df['cra'][0:10], df['year'][4791:4801].reset_index(drop=True), \
                    df['cra'][4791:4801].reset_index(drop=True), df['error'][0:10], df['error'][4791:4801].reset_index(drop=True), df)
        #df_smooth.to_csv('LOCal13_' + 'lat=' + str(lat) + 'lon=' + str(lon) + '.csv', index=False, header=True)
	return invalid_location(df_smooth, lat, lon)

    
if __name__ == '__main__':
    app.run()









   

