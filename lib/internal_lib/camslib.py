#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2019 Mundi Web Services
# Licensed under the 3-Clause BSD License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# https://opensource.org/licenses/BSD-3-Clause
#
# Author : Loona Nouvellon
#
# Contact email: loona.nouvellon@atos.net
# =============================================================================

import datetime
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import timedelta
from matplotlib.colors import ListedColormap
from matplotlib.pyplot import figure
from mpl_toolkits.basemap import Basemap
from PIL import Image

import requests
import ipywidgets as widgets
from IPython.display import display,clear_output

from owslib.wcs import WebCoverageService
from owslib.wms import WebMapService

server_url = "https://geoservices.regional.atmosphere.copernicus.eu/services/"
dlserver = "https://download.regional.atmosphere.copernicus.eu/services/CAMS50?"
    
methods = ["FORECAST", "ANALYSIS"]
pollens = ["BIRCHPOLLEN", "OLIVEPOLLEN", "GRASSPOLLEN", "RAGWEEDPOLLEN"]
species = ["O3", "CO", "NH3", "NO", "NO2", "NMVOC", "PANs", "PM10", "PM2.5", "SO2" ] + pollens
models = ["ENSEMBLE", "CHIMERE", "EMEP", "EURAD", "LOTOSEUROS", "MATCH", "MOCAGE", "SILAM"]
levels = [0,  50, 250, 500, 1000, 2000, 3000, 5000]

# ----------------------------------------------------------------
#  CAMS methods
# ----------------------------------------------------------------
def getServiceUrl(method, model, service, token):
    if model in models and method in methods:
        return server_url + "CAMS50-" + model + "-" + method +"-01-EUROPE-" + service  + "?token=" + token

# get your token
def getToken(username, password):
    response = requests.get(server_url + "GetAPIKey?username=" + username + "&password=" + password)
    return response.text.replace('<', '>').split('>')[2]

# display a map from a grib file
def plotGrib(grb, title, vmin = None, vmax = None, bbox=None, cmap=None):
    if bbox!=None:
        data, lats, lons = grb.data(lon1= bbox[0], lon2=bbox[2], lat1=bbox[1],lat2=bbox[3])
    else:
        data = grb.values
        lats,lons = grb.latlons() #Get the longitudes and the latitudes of the Grib file

    #Set the unit
    unit = 'kg/m3'
    if species in pollens:
        unit = 'm-3'

    figure(num=None, figsize=(14, 8))

    #Create a basemap with the coordinates of the bbox
    m=Basemap(projection='cyl',lat_ts=10,llcrnrlon=lons.min(), \
      urcrnrlon=lons.max(),llcrnrlat=lats.min(),urcrnrlat=lats.max(), \
      resolution='l') 

    x, y = m(lons, lats)

    m.drawcoastlines()
    m.drawcountries()

    m.bluemarble()
    
    #List of colors used for the colormap
    cols = [(0, 0, 0, 0), (0.01,0.36,0.82), (0,0.5,1), \
            (0,1,1), (0,1,0.5), (0,1,0), (0.5,1,0), (1,1,0), \
            (0.94, 0.6, 0.06), (1,0.5,0), (0.9,0.24,0), (1,0,0)]

    #Create a colormap
    cmap = ListedColormap(cols)
    
    #Color the map
    if vmin == None:
        vmin = np.amin(grb.values)
    if vmax == None:
        vmax = np.amax(grb.values)
        
    levels = np.linspace(vmin, vmax, 100)
    cs = m.contourf(x, y, data, levels, cmap = cmap, vmin=vmin, vmax = vmax, norm = colors.PowerNorm(gamma=2/3)) 
    
    #Put a title to the figure
    plt.title(title) 

    #Display the colorbar
    clb = plt.colorbar(cs,orientation='vertical', label=unit) 

    #Display the map
    return(plt)

#Define the widgets for the geographical area
def geographical_area_tab():
    lonmin= widgets.FloatText(value=-24.95, description='Long min:', step=0.01) 
    latmin= widgets.FloatText(value= 30.05, description='Lat min:', step=0.01) 
    lonmax= widgets.FloatText(value=44.95, description='Long max:', step=0.01) 
    latmax= widgets.FloatText(value=69.95, description='Lat max:', step=0.01) 

    bbox_menu = widgets.VBox([lonmin, latmin, lonmax, latmax])
    country_menu = widgets.Text(placeholder='Ex: Germany, Spain...')

    children = [bbox_menu, widgets.VBox([widgets.Label(value="Enter a country:"), country_menu])]

    tab = widgets.Tab()
    tab.children = children
    tab.set_title(0,'Bounding Box')
    tab.set_title(1,'Country')
    return tab, lonmin, latmin, lonmax, latmax, country_menu


# ----------------------------------------------------------------
#  CAMS Web Coverage Service class
# ----------------------------------------------------------------
class cams_wcs():

    # Download a coverage in Grib 
    def downloadCoverage(wcs, id, time, _subsets_, filename):
        #Get the data
        output = wcs.getCoverage(identifier=[id],
                              grid=0.1,
                              subset='time(' + time + ')',
                              subsets=_subsets_,
                              format='application/x-grib')

        #Get the destination folder path
        dir = '/home/jovyan/work/cams_data/cams_europe_services/02_WCS_example/'

        #Create the folder if it doesn't exist
        if not os.path.exists(dir):
            os.makedirs(dir)
            
        #Create a file
        f = open(os.path.join(dir, filename),'wb')
        f.write(output.read())
        f.close()
    
    
    def displayMap(method, model, token):

        url = getServiceUrl(method, model, 'WCS', token)
        wcs = WebCoverageService(url, version='2.0.1')

        layers_menu = widgets.Dropdown(
            options=list(wcs.contents),
            value=list(wcs.contents)[0],
            description='Layer:',
            disabled=False,
        )

        def getValidDates(lay):
            gml = '{http://www.opengis.net/gml/3.2}'
            layer = wcs.contents[lay]
            descCov = wcs.getDescribeCoverage(lay)

            def timePosition(pos):
                #Find the time position in Describe Coverage
                pos = descCov[0].find( gml + 'boundedBy/' + gml +'EnvelopeWithTimePeriod/' + gml + pos).text
                #Return the respective date
                return datetime.datetime.strptime(pos.replace('.', ':'), '%Y-%m-%dT%H:%M:%SZ')

            #Get the begin and end positions
            dt = timePosition('beginPosition')
            enddt = timePosition('endPosition')

            #Get all valid dates
            validDates = []
            while dt <= enddt:
                validDates.append(dt)
                dt = dt + timedelta(hours=1)
            return validDates

        def getAltitudes(lay):
            layer = wcs.contents[lay]
            descCov = wcs.getDescribeCoverage(lay) 
            gml = '{http://www.opengis.net/gml/3.2}'

            #Select an altitude only if dimension = 4
            altitudes = [0]
            if layer.grid.dimension == 4:
                rgrid = '{http://www.opengis.net/gml/3.3/rgrid}'
                coefficients = descCov[0].findall(gml + 'domainSet/' + rgrid + 'ReferenceableGridByVectors/' + rgrid + 'generalGridAxis')[2].find( rgrid + 'GeneralGridAxis/' + rgrid + 'coefficients')
                altitudes = coefficients.text.split(' ')
            return altitudes

        layer_name =  layers_menu.value
        validDates = getValidDates(layer_name)

        times_menu = widgets.Dropdown(
            options=validDates,
            value=validDates[0],
            description='Validity time:',
            disabled=False,
        )

        heigth_menu = widgets.Dropdown(
            options= getAltitudes(layer_name),
            value=getAltitudes(layer_name)[0],
            description='Altitude :',
            disabled=False,
        )

        def handle_layers_menu_change(change):
            times_menu.options=getValidDates(change.new)
            times_menu.value=getValidDates(change.new)[0] 
            heigth_menu.options=getAltitudes(change.new)
            heigth_menu.value=getAltitudes(change.new)[0] 

        layers_menu.observe(handle_layers_menu_change, names='value')

        display(layers_menu, times_menu, heigth_menu)
    
        tab, lonmin, latmin, lonmax, latmax, country_menu = geographical_area_tab()
        display(widgets.Label(value="Select a geographical area in Europe:"), tab)

        #Display the validate button
        out=widgets.Output()
        button=widgets.Button(description='Validate')
        vbox=widgets.VBox([button, out])
        display(vbox)

        def click(b):
            layer_name = layers_menu.value
            layer = wcs.contents[layer_name]

            #Define request parameters
            time = datetime.datetime.strftime( times_menu.value,'%Y-%m-%dT%H:%M:%SZ')

            #Define the bbox with the selected values
            if (tab.selected_index == 0):
                bbox = (lonmin.value, latmin.value, lonmax.value, latmax.value)
            else:
                 polygon, bbox = polygon_bbox_country(country_menu.value)
            
            subsets = [('lat',bbox[1],bbox[3]), ('long',bbox[0],bbox[2])]
            
            if (layer.grid.dimension == 4):
                subsets.append(('height', heigth_menu.value))

            dir = '/home/jovyan/work/cams_data/cams_europe_services/02_WCS_example/'
            name = model + '_' + method + '_' + layer_name + '.grib' 
            filename = os.path.join(dir, name)

            #Download the data
            cams_wcs.downloadCoverage(wcs, layer_name, time, subsets, filename)

            import pygrib
            grib = dir +'/' + name
            grbs = pygrib.open(grib)
            grb = grbs.select()[0]

            with out:
                plt.close()
                clear_output()
                plotGrib(grb, layer_name.replace('_', ' ')).show()

        button.on_click(click)

# ----------------------------------------------------------------
#  CAMS Web Map Service class
# ----------------------------------------------------------------
class cams_wms():
    
    def getMapImage(wms, layer, bbox, size, time, elevation):
        #Get the map
        output = wms.getmap(layers = [layer.name], 
                         styles = layer.styles, 
                         srs = layer.crsOptions[0], 
                         bbox = bbox, 
                         size = size, 
                         time = time, 
                         elevation = elevation,
                         format = 'image/png')

        #Open the image
        return(Image.open(output))

    def getLegend(layer):
        from io import BytesIO

        #Get the style's name
        key = list(layer.styles.keys())[0]

        #Get the legend
        resp = requests.get(layer.styles.get(key).get('legend'))

        #Open the image
        return(Image.open(BytesIO(resp.content)))
    
    def plotMapLegend(image, legendImg, title, bbox):
        fig = plt.figure(figsize=(10, 6))

        fig.subplots_adjust(0, 0, 6, 4)
        #Create a Basemap
        m =  Basemap(projection='cyl', llcrnrlon=bbox[0], 
                       llcrnrlat=bbox[1], urcrnrlon=bbox[2],
                       urcrnrlat=bbox[3], epsg=4326, resolution='l') 

        m.drawcoastlines()
        m.drawcountries()
        
        #Display the image over the map
        m.imshow(np.array(image.transpose(Image.FLIP_TOP_BOTTOM)))

        #Put a title to the map
        plt.title(title, fontsize=20)

        #Add the legend
        fig.subplots_adjust(0, 0, 1, 1)
        legend = fig.add_axes([0., 0., 2.5, 1])
        legend.imshow(legendImg, origin = 'upper')
        legend.set_xticks([])
        legend.set_yticks([])

        return plt

    def displayMap(method, model, token):
        
        url = getServiceUrl(method, model, 'WMS', token)
        wms = WebMapService(url, version='1.3.0')

        layers_menu = widgets.Dropdown(
            options=list(wms.contents),
            value=list(wms.contents)[0],
            description='Layer:',
            disabled=False,
        )

        display(layers_menu)

        layer =  wms.contents[layers_menu.value]
        
        #Display the valid dates
        times_menu = widgets.Dropdown(
            options=layer.timepositions,
            value=layer.timepositions[0],
            description='Validity time:',
            disabled=False,
        )

        #Choose an elevation only if elevations is not None
        elevations = [0]
        if layer.elevations != None: 
            elevations = layer.elevations

        elevations_menu = widgets.Dropdown(
            options=elevations,
            value=elevations[0],
            description='Elevation:',
            disabled=False,
        )

        height_menu = widgets.IntText(
            value=495,
            description='Height:',
            disabled=False)

        width_menu = widgets.IntText(
            value=810,
            description='Width:',
            disabled=False)

        def handle_layers_menu_change(change):
            layer =  wms.contents[change.new]

            times_menu.options=layer.timepositions
            times_menu.value= layer.timepositions[0] 

            elevations = [0]
            if layer.elevations != None:
                elevations = layer.elevations
            elevations_menu.options=elevations
            elevations_menu.value=elevations[0]

        layers_menu.observe(handle_layers_menu_change, names='value')

        display(times_menu, elevations_menu, widgets.VBox([widgets.Label(value="Choose the image size:"), height_menu, width_menu]))

        tab, lonmin, latmin, lonmax, latmax, country_menu = geographical_area_tab()

        display(widgets.Label(value="Select a geographical area in Europe:"), tab)

        #Display the validate button
        out=widgets.Output()
        button=widgets.Button(description='Validate')
        vbox=widgets.VBox([button, out])
        display(vbox)

        def click(b):
            layer = wms.contents[layers_menu.value]

            #Define the bbox with the selected values
            if (tab.selected_index==0):
                bbox = (lonmin.value, latmin.value, lonmax.value, latmax.value)
            else:
                 polygon, bbox = polygon_bbox_country(country_menu.value)
                    
            #Get the image
            img = cams_wms.getMapImage(wms, layer, bbox, (width_menu.value, height_menu.value), times_menu.value, elevations_menu.value)

            #Open the image
            legendGraphic = cams_wms.getLegend(layer)

            with out:
                plt.close()
                clear_output()
                cams_wms.plotMapLegend(img, legendGraphic, layer.name.replace('_', ' ') , bbox).show()

        button.on_click(click)

# ----------------------------------------------------------------
#  CAMS download web service class
# ----------------------------------------------------------------
class cams_download():
        
    def downloadPackage(token, model, method, pollutant, time, date, level):  
                
        leveltype = "ALLLEVELS"
        if level == 0:
            leveltype = "SURFACE"

        dlurl = dlserver + "&token=" + token + "&grid=0.1&model=" + model + "&package=" + method + "_" +  \
            pollutant + "_" + leveltype + "&time=" + time +"&referencetime=" + date + "T00:00:00Z&format=GRIB2"

        resp = requests.get(dlurl)
        
        data_name = model + '_' + method + '_' + pollutant + '_' + date + '_' + time + '_level_' + str(level)

        #Get the destination folder path
        dir = '/home/jovyan/work/cams_data/cams_europe_services/03_Download_packaged_data/' + \
            model + '_' + method + '_' + pollutant 
            
        #Create the folder if it doesn't exist
        if not os.path.exists(dir):
            os.makedirs(dir)

        filename = data_name + '.grib'

        #Create a file
        f = open(os.path.join(dir, filename),'wb')
        f.write(resp.content)
        f.close()


    def displayMap(token):
        
        times = { "FORECAST": ["0H24H", "25H48H", "49H72H", "73H96H"], "ANALYSIS": ["-24H-1H"]}

        methods_menu  = widgets.Dropdown(
            options=methods,
            value=methods[0],
            description='Method:',
            disabled=False,
        )

        models_menu = widgets.Dropdown(
            options=models,
            value=models[0],
            description='Model:',
            disabled=False,
        )
        
        pollutants = species
        if (methods_menu.value == 'ANALYSIS'):
            pollutants = [i for i in species if i not in pollens]

        species_menu = widgets.Dropdown(
            options=pollutants,
            value=pollutants[0],
            description='Species:',
            disabled=False,
        )

        times_menu = widgets.Dropdown(
            options=times[methods_menu.value],
            value=times[methods_menu.value][0],
            description='Times:',
            disabled=False,
        )
        
        available_levels = levels
        if species_menu.value in pollens:
            available_levels = [0]
    
        levels_menu = widgets.Dropdown(
            options=available_levels,
            value=available_levels[0],
            description='Level:',
            disabled=False,
        )

        def handle_methods_menu_change(change):
            pollutants = species
            if (change.new == 'ANALYSIS'):
                pollutants = [i for i in species if i not in pollens]
            species_menu.options=pollutants
            species_menu.value=pollutants[0]            
            times_menu.options=times[change.new]
            times_menu.value=times[change.new][0]

        def handle_species_menu_change(change):
            available_levels = levels
            if change.new in pollens:
                available_levels = [0]
            levels_menu.options=available_levels
            levels_menu.value=available_levels[0]

        methods_menu.observe(handle_methods_menu_change, names='value')
        species_menu.observe(handle_species_menu_change, names='value')
         
        from IPython.display import Image

        dates_menu = widgets.DatePicker(
            description='Date:',
            value = datetime.date.today() - timedelta(days=30),
            disabled=False
        )

        display(methods_menu, models_menu, species_menu, times_menu, dates_menu, levels_menu)
        
        tab, lonmin, latmin, lonmax, latmax, country_menu = geographical_area_tab()

        display(widgets.Label(value="Select a geographical area in Europe:"), tab)

        #Display the validate button
        out=widgets.Output()
        button=widgets.Button(description='Validate')
        vbox=widgets.VBox([button, out])
        display(vbox)

        def click(b):
            
            model = models_menu.value
            method = methods_menu.value
            pollutant = species_menu.value
            date = dates_menu.value.strftime("%Y-%m-%d")
            time = times_menu.value
            level = levels_menu.value

            cams_download.downloadPackage(token, model, method, pollutant, time, date, level)

            data_name = model + '_' + method + '_' + pollutant + '_' + date + '_' + time + '_level_' + str(level)

            #Define the bbox with the selected values
            if (tab.selected_index == 0):
                bbox = (lonmin.value, latmin.value, lonmax.value, latmax.value)
            else:
                 polygon, bbox = polygon_bbox_country(country_menu.value)
                    
            #Get the destination folder path
            dir = '/home/jovyan/work/cams_data/cams_europe_services/03_Download_packaged_data/' + \
                model + '_' + method + '_' + pollutant 

            #Open the GRIB file
            import pygrib
            grbs = pygrib.open(os.path.join(dir, data_name + '.grib'))

            with out:
                clear_output()
                
                if (grbs.messages==0):
                    leveltype = "ALLLEVELS"
                    if level == 0:
                        leveltype = "SURFACE"
                    print('No data available in the file')
                    return 0
                grb = grbs.select()[0]

                vmax = np.amax(grb.values)

                result_filename = data_name + "_result.gif"

                gribs = grbs.select(level=levels_menu.value)
                
                f = widgets.FloatProgress(min=0, max=len(gribs) - 1)
                label = widgets.Label(value="Downloading 0%")

                display(label, f)
                nb = 0
                
                #Create a new image for each time
                for grb in gribs:
                    time = grb['stepRange']
                    plt = plotGrib(grb, pollutant + ' ' + date + ' time: ' + time + ' level: ' + str(levels_menu.value), \
                                   0, vmax, bbox=bbox)
                    plt.savefig(os.path.join(dir, model + '_' + method + '_' + pollutant + '_nb_' + str(nb) + '.png'))
                    plt.close()
                    nb += 1
                    f.value += 1
                    label.value = 'Downloading ' + str(round(f.value/f.max*100)) + '%'

                #Create a GIF 
                import imageio 

                images = [ imageio.imread(os.path.join(dir,  model + '_' + method + '_' + \
                                                       pollutant + '_nb_' + str(i) + '.png')) for i in range(1, len(gribs))]
                imageio.mimsave(os.path.join(dir, result_filename), images, 'GIF', duration=0.2)
                
                clear_output()
                display(Image(os.path.join(dir, result_filename)))

        button.on_click(click)