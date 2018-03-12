# local_curves

## Description

REST API for the generation of local marine curves to be used in the process of radiocarbon calibration. The local curves, 
named **LOCal13**, are based on the existing calibration curves presented by [Reimer et al. (2013)](https://journals.uair.arizona.edu/index.php/radiocarbon/article/view/16947) and constructed accordingly 
to the spatial resolution of the marine reservoir age model presented by [Butzin et al. (2017)](http://onlinelibrary.wiley.com/doi/10.1002/2017GL074688/full). 
A complete description can be found in Alves et al. (2018). 

## Dependencies  

* Python 2.7.14
* Pandas
* Numpy
* csv
* netCDF4
* flask

## Instructions 

All the necessary data was uploaded as supplementary material for Alves et al. (2018). Start by running filter.py to generate the filter.csv file. 
This is used by api.py to create local curves. Use api.py to run the REST API. 

## Overview

You can query the API using the route specified in api.py and choosing the geographic coordinates of your study region.
The API will return **"Year cal BP"**, **"Radiocarbon Determination (BP)"** and **"Uncertainty (BP)"** in JSON. If you choose the
coordinates of a place which is not available in the underlying model, data for the closest location will be returned instead. If you
use an incorrect URL format to query the REST API, you will a 404 HTTP status response.

## Example query using URL parameters

http://127.0.0.1:5000/coordinates?lat=0&lon=0
