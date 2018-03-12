# local_curves

## Description

REST API for the generation of local marine curves to be used in the process of radiocarbon calibration. The local curves, 
named **LOCal13**, are based on the existing calibration curves presented by [Reimer et al. (2013)](https://journals.uair.arizona.edu/index.php/radiocarbon/article/view/16947) and constructed accordingly 
to the spatial resolution of the marine reservoir age model presented by [Butzin et al. (2017)](http://onlinelibrary.wiley.com/doi/10.1002/2017GL074688/full). 
A complete description can be found in Alves et al. (2018). 

## Dependencies  

* Python 2.7.14
* Pandas 0.20.3
* Numpy  1.11.3 
* netCDF4 1.3.1
* flask   0.12.2

## Instructions 

All the necessary data was uploaded as supplementary material for Alves et al. (2018). Start by running filter.py to generate the filter.csv file. 
This is used by api.py to create local curves. Use api.py to run the REST API. 

## GET /coordinates?lat={latitude}&lon={longitude}

You can query the API using the route specified in api.py and choosing the geographic coordinates of your study region.
The API will return details in JSON and a HTML table with **"Year cal BP"**, **"Radiocarbon Determination (BP)"** and **"Uncertainty (BP)"**: 

![True](https://user-images.githubusercontent.com/34550058/37311339-c857c9a4-263e-11e8-894c-871c28d2e408.jpg)

If you choose the coordinates of a place which is not available in the underlying model, data for the closest location will be returned instead:

![False](https://user-images.githubusercontent.com/34550058/37311377-e75db8cc-263e-11e8-84c1-df94526481ed.jpg)

If you use an incorrect URL format to query the REST API, you will a 404 HTTP status response:

![Error](https://user-images.githubusercontent.com/34550058/37311543-96010cc6-263f-11e8-9e95-ca4c65cb8e1a.png)




