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

All the necessary data was uploaded as supplementary material for Alves et al. (2018). Data and code should be in the same folder. The api.py code creates local curves. Use api.py to run the REST API. 

## GET /coordinates?lat={latitude}&lon={longitude}
You can query the API using the route specified in api.py and choosing the geographic coordinates of your study region. Alternatively, you can use the boxes to enter the coordinate values.

![Box](https://github.com/eduqq/local_curves/Images/box.png)

## Examples:

The API will return details in JSON and a HTML table with **"Year cal BP"**, **"Radiocarbon Determination (BP)"** and **"Uncertainty (BP)"**: 

## http://127.0.0.1:5000/coordinates?lat=1.25&lon=0

![True](https://github.com/eduqq/local_curves/Images/true.png)

If you choose the coordinates of a place which is not available in the underlying model, data for the closest location will be returned instead:

## http://127.0.0.1:5000/coordinates?lat=0&lon=0

![False](https://github.com/eduqq/local_curves/Images/false.png)

If you use an incorrect URL format to query the REST API, you will get a 404 HTTP status response:

## http://127.0.0.1:5000/coordinate?lat=0&lon=0

![Error](https://github.com/eduqq/local_curves/Images/error.png)




