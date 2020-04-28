# Welcome to Mundi Jupyter Notebook

### Important notice

- your session will stop after one hour of inactivity
- only elements in _work_ directory can be saved

### License

Copyright (c) 2019 Mundi Web Services
Licensed under the 3-Clause BSD License; you may not use the below listed files except in compliance with the License.
You may obtain a copy of the License at:
https://opensource.org/licenses/BSD-3-Clause

### Folders contents

* _/home/jovyan/lib_: contains visible libraries, listed below. It is read-only.
    * _mundilib_: Mundi library. Based on [OWSLib](https://geopython.github.io/OWSLib/) Python package, compliant with Open Geospatial Consortium (OGC) web service (hence OWS) interface standards and their related content models.
                 
* _/home/jovyan/lib/internal_lib_:  contains protected libraries. Not visible but can be executed for/by users.
    * _camslib_: CAMS (Copernicus Atmosphere Monitoring Service) library. See an example of how to use it in notebook _cams_europe_services.ipynb_.
                     
            - ---------------------------------------------------------------------------------------------------------------
            | Class               | Function                           | Description                                        |
            - ---------------------------------------------------------------------------------------------------------------
            |                     |                                    |                                                    |
            |                     | getToken(username, password)       | Returns a token                                    |
            |                     |                                    |                                                    |
            |                     | getServiceUrl(method,              | Returns the service url corresponding to the       |
            |                     |  model, service, token)            | selected service (WCS or WMS), method (See the     |
            |                     |                                    | list modelst) and model (See the list models).     |
            |                     |                                    | A valid token is required.                         |
            |                     |                                    |                                                    |
            |                     | plotGrib(grb, title, vmin = None,  | Creates and returns a figure with a map displaying |
            |                     | vmax = None, bbox=None, cmap=None) | from a GRIB file                                   |
            |                     |                                    |                                                    |
            |                     | geographical_area_tab()            | Creates a widget for to select a geographical area.|
            |                     |                                    |                                                    |
            - ---------------------------------------------------------------------------------------------------------------
            |                     |                                    |                                                    |
            |                     | downloadCoverage(wcs, id, time,    | Downloads a coverage in Grib format corresponding  |
            |                     |   _subsets_, filename)             | to the selected parameters                         |
            |                     |                                    |                                                    |
            | cams_wcs            | displayMap(method, model, token)   | Displays a map corresponding to the selected method|
            |                     |                                    | and model. A valid token is required.              |
            |                     |                                    |                                                    |
            |                     | plotGrib(grb, title, vmin = None,  | Creates and returns a figure with a map displaying |
            |                     | vmax = None, bbox=None, cmap=None) | from a GRIB file                                   |
            |                     |                                    |                                                    |
            - ---------------------------------------------------------------------------------------------------------------
            |                     |                                    |                                                    |
            |                     | getMapImage(wms, layer, bbox, size,| Returns a image corresponding to the selected      |
            |                     |  time, elevation)                  | parameters                                         |
            |                     |                                    |                                                    |
            |                     | getLegend(layer)                   | Returns the legend corresponding to the layer      |
            | cams_wms            |                                    |                                                    |
            |                     | displayMap(method, model, token)   | Displays a map corresponding to the selected method|
            |                     |                                    | and model. A valid token is required.              |
            |                     |                                    |                                                    |
            |                     | plotMapLegend(image, legendImg,    | Creates and returns a figure with a map displaying |
            |                     | title, bbox)                       | the image and its legend                           |
            |                     |                                    |                                                    |
            - ---------------------------------------------------------------------------------------------------------------
            |                     |                                    |                                                    |
            |                     | downloadPackage(token, model,      | Downloads a packaged data in Grib format           |
            |                     |  method, pollutant, time, date,    | corresponding to the selected parameters           |
            |                     |  level)                            |                                                    |
            | cams_download       |                                    |                                                    |
            |                     | getLegend(layer)                   | Returns the legend corresponding to the layer      |
            |                     |                                    |                                                    |
            |                     | displayMap(token)                  | Displays a map. A valid token is required.         |
            |                     |                                    |                                                    |         
            - ---------------------------------------------------------------------------------------------------------------
            
    * _cmemslib_: CMEMS (Copernicus Marine Environment Monitoring Service) library. See an example of how to use it in _cmems_use_case.ipynb_.
        
             ----------------------------------------------------------------------------------------------------------------
            | Class               | Function                           | Description                                        |
            - ---------------------------------------------------------------------------------------------------------------
            |                     |                       MODEL AND SATELLITE PRODUCTS                                      |
            |                     | ----------------------------------------------------------------------------------------|     
            |                     | Cmems.download_Product()           | function that allows to download NetCDF files      |
            |                     |                                    | from CMEMS catalog products(model or satellite).   |
            |                     |                                    | The download procedure is done using               |   
            |                     |                                    | the ftp protocol.                                  |
            |                     |                                    | e.g. : case 1:                                     |
            |                     |                                    | update=Cmems.download_Product(user,password        |
            |                     |                                    |                                    ,'Model')       |
            |                     |                                    |        case 2:                                     |
            |                     |                                    | update=Cmems.download_Product(user,password,       |
            |                     |                                    |                                 'Satellite')       |
            |                     |                                    |                                                    |
            |                     |                                    |                                                    |
            |                     | Cmems.read_File()                  | function that reads the downloaded NetCDF file.    |
            | Cmems()             |                                    | Usable only for model and satellite products       |
            |                     |                                    | e.g. : case 1:                                     |
            |                     |                                    | ds,selected_list,selected_list_name,file_name      | 
            |                     |                                    |               =Cmems.read_File(update,'Model')     |
            |                     |                                    |        case 2 :                                    |
            |                     |                                    | ds,selected_list,selected_list_name,file_name      |
            |                     |                                    |               =Cmems.read_File(update,'Satellite') |
            |                     |                                    |                                                    |
            |                     |                                    |                                                    |
            |                     | Cmems.display_param_model()        | function that displays the parameters of           |
            |                     |                                    | the downloaded file (for model product).           |
            |                     |                                    | the display is in progress, for now it works       |
            |                     |                                    | only for Baltic Sea products                       |
            |                     |                                    | e.g. :                                             |
            |                     |                                    | update_disp=Cmems.display_param_model(ds           |
            |                     |                                    |                 ,selected_list,selected_list_name) |
            |                     |                                    |                                                    |
            |                     | Cmems.display_param_satellite()    | function that displays the parameters of the       |
            |                     |                                    | downloaded file (for satellite product).           |
            |                     |                                    | the display is in progress,for now it works only   |
            |                     |                                    | for Baltic Sea products                            |
            |                     |                                    | e.g. :                                             | 
            |                     |                                    | Cmems.display_param_satellite(ds2,selected_list2   |
            |                     |                                    |  ,file_name2,scale_min,scale_max,colormap_scale)   | 
            -                     -------------------------------------------------------------------------------------------
            |                     |                              INSITU PRODUCT                                             | 
            -                     -------------------------------------------------------------------------------------------
            |                     | Cmems.Insitu_Products_download()   | function that allows to download NetCDF files      |
            |                     |                                    | from the insitu product.                           |
            |                     |                                    | The download procedure is done using               |
            |                     |                                    | the ftp protocol                                   |
            |                     |                                    | e.g. :                                             |
            |                     |                                    | update3=Cmems.Insitu_Products_download             |
            |                     |                                    |                                (host,user,password)|
            |                     |                                    |                                                    |
            |                     |                                    |                                                    |
            |                     | Cmems.Insitu_read_files()          | function that reads the downloaded NetCDF file     |
            |                     |                                    | for insitu product.                                |
            |                     |                                    | e.g. :                                             |
            |                     |                                    | All_ds=Cmems.Insitu_read_files(dataset_all)        |
            |                     |                                    |                                                    |
            |                     | Cmems.display_Insitu_product()     | function that displays the parameters of the       |
            |                     |                                    | downloaded files (for insitu product).             |
            |                     |                                    | e.g. :                                             |
            |                     |                                    | Cmems.display_Insitu_product(All_ds,               |
            |                     |                                    |   selected_product,selected_parameter,scale_min,   |
            |                     |                                    |                          scale_max,colormap_scale) |
            |                     |                                    |                                                    |
            -                     -------------------------------------------------------------------------------------------
            |                     |                                    |                                                    |
            |                     | Cmems.Display_all_figures()        | function that displays all the obtained results    |
            |                     |                                    | together                                           |
            |                     |                                    |                                                    |
            |                     | Cmems.Display_all_figures_folium() | function that displays all the obtained results    |
            |                     |                                    | on a interactive map                               |
            - ---------------------------------------------------------------------------------------------------------------
           

* _/home/jovyan/public_: contains Notebook examples. All users have read and execute permissions.

            - ------------------------------------------------------------------------------
            | Notebook name           | Description                                        |
            - ------------------------------------------------------------------------------
            | mundi_data_metadata     | Available data & metadata on Mundi                 |
            - ------------------------------------------------------------------------------            
            |                         | Web services. Discovery and usage examples:        |
            |                         |                                                    |            
            | mundi_csw               |    Catalogue Service Web                           |
            |                         |                                                    |
            | mundi_wcs               |    Web Coverage Service                            |
            | mundi_wfs               |    Web Feature Service                             |
            | mundi_wms               |    Web Map Service                                 |
            | mundi_wmts              |    Web Map Tile Service                            |
            |                         |                                                    |
            - ------------------------------------------------------------------------------
            | mundi_opensearch        | Examples of opensearch requests                    |
            - ------------------------------------------------------------------------------
            | mundi_gdal              | Visualisation of an image from Toulouse as         |
            |                         | an histogram from its raster.                      |
            - ------------------------------------------------------------------------------
            | mundi_exceptions        | Examples of Mundi raised exception                 |            
            | mundi_video             | Just for fun!                                      |
            - ------------------------------------------------------------------------------
            | mundi_country_polygon   | Example of how to get and visualize polygon,bbox   |
            |                         | and a geojson file from a country name             |
            | mundi_wms_city_polygon  | Example of how to get and visualize polygon, bbox  |
            |                         | and a satellite image from a city name             |
            | mundi_shapefile         | Example of how to create, read, and display a      |
            |                         | shapefile on a map                                 |
            - ------------------------------------------------------------------------------
            |                         | CAMS web services. Discovery and usage examples:   |
            |                         |                                                    |            
            | cams_europe_services    | Usage examples of Web Map Service, Web Coverage    |
            |                         | Service and Download API for Europe                |
            | cams_ecmwfapi           | Usage example of ECMWF api to download and         |
            |                         | display CAMS data                                  |
            |                         |                                                    |
            - ------------------------------------------------------------------------------
            |                         | CMEMS web services. Examples of interaction with   |
            |                         |                      CMEMS catalog products:       |
            |                         |                                                    |            
            | cmems_use_case          | Examples of how to download, read and display      |
            |                         | CMEMS data using NetCDF (Network Common Data Form) |
            |                         | files                                              |
            - ------------------------------------------------------------------------------
            
* _/home/jovyan/work/_: personnal folder that will persist through Jupyter Notebook sessions. Store anything you want to keep in that folder.

### Installed libraries

#### List them all

Use `conda list` shell command to list all installed packages & version. A small sample:

            - -------------------------------------------------------------------------------------------------------------
            | Package name            | Description                                        | www                          |
            - -------------------------------------------------------------------------------------------------------------
            | gdal                    | Geospatial Data Abstraction library                | https://www.gdal.org/        |  
            | matplotlib              | Python 2D plotting library                         | https://matplotlib.org/      | 
            | NumPy                   | Base N-dimensional array package                   | http://www.numpy.org/        |        
            | pandas                  | Python Data structures & analysis library          | https://pandas.pydata.org/   | 
            | s3cmd                   | Command line tool for managing Amazon S3           | https://s3tools.org/s3cmd    |       
            - -------------------------------------------------------------------------------------------------------------

#### Install new ones
            
To install a new library a notebook cell like the following can be included:

`!pip install <package_name>`

The notebook environment also supports opening a terminal, in which this command can be executed as well. 


### Clipboard usage

    Dot   + Tab                  : completion in notebook
    MAJ   + Insert               : paste text from clipboard
    Shift + <right_mouse_button> : access to clipboard


### Webography

Bounding box finder : http://bboxfinder.com
