# Library containing all the useful functions for the GIF_Creation Notebook
# Author : ALCOUFFE Rémy
# Contact email : remy.alcouffe@atos.net


#PYTHONPATH Settings
import sys
sys.path.append("/home/jovyan/lib")

import datetime
import imageio
import ipywidgets as widgets
import numpy as np
import os
import urllib
import xml.etree.ElementTree as ET

from IPython.display import clear_output, HTML
from mundilib import MundiCatalogue
from PIL import Image, ImageDraw, ImageFont
from utils import city_polygon_bbox, country_polygon_bbox

# --------------------------
#  Global Variables
# --------------------------

#TO-DO Add other layers when available
DICT_LAYER = {'Sentinel1-GRD':[('IW_VV',0),('IW_VV_DB',2),('IW_VH',4),('IW-VH-DB',5)],
              'Sentinel2-L1C':[('1_NATURAL_COLOR',1),('2_COLOR_INFRARED__VEGETATION_',2),('3_FALSE_COLOR__URBAN_',3),
                               ('4_AGRICULTURE',4),('6_MOISTURE_INDEX',6),('7_GEOLOGY',7),('8_BATHYMETRIC',8),('09-NDVI',0),
                               ('90_ATMOSPHERIC_PENETRATION',9),('91_SWIR',10),('92_NDWI',11),('93-SWIR-2-11-12',12),
                               ('B01',13),('B02',14),('B03',15),('B04',16),('B05',17),('B06',18),('B07',19),('B08',20),
                               ('B09',21),('B10',22),('B11',23),('B12',24),('B8A',25)],
              'Sentinel2-L2A':[('SCL',0),('AGRICULTURE',1),('ATMOSPHERIC_PENETRATION',2),('BATHYMETRIC',3),('COLOR_INFRARED',4),
                               ('COLOR_INFRARED_URBAN',5),('GEOLOGY',6),('MOISTURE_INDEX',7),('SWIR',8),('TRUE_COLOR',9),('VEGETATION_INDEX',10)],
              'Sentinel5P-L2':[('AER_AI_340_380',0),('AER_AI_340_AND_380_VISUALIZED',1),('AER_AI_354_388',2),('CH4',3),('CH4_VISUALIZED',4),
                               ('CLOUD_BASE_HEIGHT',5),('CLOUD_BASE_HEIGHT_VISUALIZED',6),('CLOUD_BASE_PRESSURE',7),
                               ('CLOUD_BASE_PRESSURE_VISUALIZED',8),('CLOUD_FRACTION ',9),('CLOUD_FRACTION_VISUALIZED',10),
                               ('CLOUD_OPTICAL_THICKNESS',11),('CLOUD_OPTICAL_THICKNESS_VISUALIZED',12),('CLOUD_TOP_HEIGHT',13),
                               ('CLOUD_TOP_HEIGHT_VISUALIZED',14),('CLOUD_TOP_PRESSURE',15),('CLOUD_TOP_PRESSURE_VISUALIZED',16),('CO',17),
                               ('CO_VISUALIZED',18),('HCHO',19),('HCHO_VISUALIZED',20),('NO2',21),('NO2_VISUALIZED',22),('O3',23),
                               ('O3_VISUALIZED',24),('SO2',25),('SO2_VISUALIZED',26)]}


# --------------------------
#  Useful functions
# --------------------------

def get_image(bbox,height,width,wms_layers,time,sattellite,collection):
    """This function makes the WMS request to MundiCatalogue to download the chosen image

    Parameters
    ----------
    bbox: numpy.array
        The BBOX of the area chosen
    height: int
        The height in pixels of the returned image
    width: int
        The width (in pixels) of the returned image
    wms_layers: int
        # of layer to extract
    time: string
        Period of time to select the image
    sattellite: string
        Sattellite chosen
    collection: string
        Colllection chosen
    
    Returns
    -------
    img:
        Link to the image to download/open
    """
    c = MundiCatalogue()
    wms = c.get_collection(sattellite).mundi_wms(collection)

    projection = 'EPSG:4326'

    layers = list(wms.contents)
    
    img = wms.getmap(layers=[wms[layers[wms_layers]].name],
                        srs=projection,
                        bbox=bbox,
                        size=(width, height),
                        format='image/png',
                        time=time,
                        showlogo=False,
                        transparent=False,
                        )
    return img

def get_date(bbox,height,width,wms_layers,time,sattellite,collection):
    """This function makes the WMS request to MundiCatalogue to download the chosen image

    Parameters
    ----------
    bbox: numpy.array
        The BBOX of the area chosen
    height: int
        The height in pixels of the returned image
    width: int
        The width (in pixels) of the returned image
    wms_layers: int
        # of layer to extract
    time: string
        Period of time to select the image
    sattellite: string
        Sattellite chosen
    collection: string
        Colllection chosen
    
    Returns
    -------
    img:
        Link to the image to download/open
    """
    date = 'XXXX-XX-XX'
    c = MundiCatalogue()
    wms = c.get_collection(sattellite).mundi_wms(collection)

    projection = 'EPSG:4326'

    layers = list(wms.contents)
    
    response = wms.getfeatureinfo(layers=[wms[layers[wms_layers]].name],
                                srs=projection,
                                bbox=bbox,
                                size=(width, height),
                                info_format='text/xml',
                                time=time,
                                showlogo=False,
                                xy = (width//2,height//2)
                        )
    
#     resp = str(response.read()).replace('\\r\\n', '')
#     resp = resp.replace('b\'', '')
#     resp = resp.replace('>\'', '>')
#     resp = resp.replace('\\n\'','')

    root = ET.fromstring(response.read())
    for child in root:
        date = child.attrib['date']
    
    return date


def add_logo(image, logo):
    """This function pastes a logo on an image

    Parameters
    ----------
    image: PIL.PngImagePlugin.PngImageFile
        The original image onto which you want to add a logo
    logo: PIL.PngImagePlugin.PngImageFile
        The logo you want to add to your image

    """
    # Resize Logo
    wsize = int(image.size[1] * 0.30)
    wpercent = (wsize / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))

    simage = logo.resize((wsize, hsize))

    # right bottom corner
    box = (int(0.08*image.size[1]),int(0.035*image.size[0]))
    image.paste(simage, box, simage)


def generate_gif(bbox,collection,layer,start_date,stop_date,download,output_name,
                 title,subtitle,delta_days,height,width,duration):
    """This functions generates the GIF file with the given parameters

    Parameters
    ----------
    bbox: numpy.array
        The BBOX of the area chosen
    collection: tuple
        tuple containing the sattellite and the collection
    layer: int
        # of layer to create the GIF
    start_date : string
        The start date of your GIF
    stop_date : string
        The stop date of your GIF
    download: boolean
        Boolean to chose either if you want to download the images or not
    output_name: string
        The name of your gif
    delta_days: int
        number of days between two images
    height: int
        The height in pixels of the returned image
    width: int
        The width (in pixels) of the returned image   

    """
    save_folder = '/home/jovyan/work/gif_images/'
    
    (sattellite,collection) = collection
    current_date = start_date
    
    # Importing Mundi_logo
    logo = Image.open(urllib.request.urlopen('https://mundiwebservices.com/build/assets/Mundi-Logo-CMYK-white.png'))
    logo.mode=('RGBA')

    clear_output(wait=True)
    k = str(int(((stop_date - current_date).days)/delta_days))
    cpt = 0
    images = []
    while current_date < stop_date:
        next_date = current_date + datetime.timedelta(delta_days,0)
        time = current_date.strftime("%Y-%m-%d") + '/' + next_date.strftime("%Y-%m-%d")
        print("\r Image #" + str(cpt) + "/" + k + " : " + time)
        img = get_image(bbox, height, width, layer, time, sattellite, collection)
        image = Image.open(img)
        image = image.convert('RGB')
        fnt = ImageFont.truetype('/home/jovyan/work/poppins-light.ttf', int(width/45))
        fnt2 = ImageFont.truetype('/home/jovyan/work/poppins-light.ttf', int(width/30))
        fnt3 = ImageFont.truetype('/home/jovyan/work/poppins-light.ttf', int(width/55))
        draw = ImageDraw.Draw(image)
        date = get_date(bbox, height, width, layer, time, sattellite, collection)
        draw.text((0.82*width,0.10*height), date, (255,255,255), fnt)
        draw.text((0.05*width,0.85*height), title, (255,255,255), fnt2)
        draw.text((0.068*width,0.93*height), subtitle, (255,255,255), fnt3)
        add_logo(image,logo)
        images.append(np.array(image))
        if download:
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
            filename = str(cpt) + '.png'
            image.save(save_folder + filename)       
        current_date = next_date
        cpt += 1
        clear_output(wait=True)
        imageio.mimsave(f'../work/{output_name}', images, duration = duration/int(k))
    print("GIF File generated !")


# --------------------------
#  Display funtions
# --------------------------


# Main Function
# By calling this function, widgets will be displayed and each time the user
# clicks on validate, a new function will be called and new widgets will be 
# displayed.
def create_gif():
    """This function allows the user to select all the parameters to create their own GIFs.
    It saves them directly on their work directory
    
    """
    
    lonmax = widgets.FloatText(value = 1.5153795, description = 'Long max:', disabled = False, step = 0.001)
    latmax = widgets.FloatText(value = 43.668708, description = 'Lat max:', disabled = False, step = 0.001)
    lonmin = widgets.FloatText(value = 1.3503956, description = 'Long min:', disabled = False, step = 0.001)
    latmin = widgets.FloatText(value = 43.532654, description = 'Lat min:', disabled = False, step = 0.001)
    
    bbox_menu = widgets.VBox([lonmax, latmax, lonmin, latmin])
    
    raw_bbox_menu = widgets.Textarea(
        value='1.5153795,43.668708,1.3503956,43.532654',
        placeholder='BBOX',
        disabled=False,
        layout=widgets.Layout(width='50%')
    )

    cities_menu = widgets.Text(placeholder = 'Ex: Toulouse, Paris, New-York...')

    children = [bbox_menu,
                widgets.VBox([
                    widgets.Label(value="Enter a city:"),
                    cities_menu
                ]),
               widgets.VBox([
                   widgets.Label(value="Enter a raw BBOX:"),
                   raw_bbox_menu
               ])]

    tab = widgets.Tab()
    tab.children = children
    tab.set_title(0, 'Bounding Box')
    tab.set_title(1, 'Cities')
    tab.set_title(2, 'Raw Bounding Box')

    global_output = widgets.Output()
    out = widgets.Output()
    button = widgets.Button(description = 'Validate')

    display(tab)
    display(button)
    display(out)
    display(global_output)

    bbox = [1.5153795, 43.668708, 1.3503956, 43.532654] # default bbox on Toulouse

    # Defines the action when the button is clicked.
    # Here the button validates the bbox, and call the next widget (collection_widget)
    def click_bbox(b):
        global bbox
        bbox = get_bbox(tab,out,lonmax,latmax,lonmin,latmin,cities_menu,raw_bbox_menu)
        with global_output:
            clear_output(wait=True)
            get_collection(bbox)
    button.on_click(click_bbox)


def get_bbox(tab,out,lonmax,latmax,lonmin,latmin,cities_menu,raw_bbox_menu):
    """This function validates the bbox and display it to the user

    Parameters
    ----------
    tab: ipywidgets.Tab()
        Tab widget for selection between BBOX and cities
    out: ipywidgets.Output()
        Output widget to display the BBOX to the user
    lonmax,latmax,lonmin,latmin: ipywidgets.FloatText()
        Widgets containing the values of the BBOX entered by user
    cities_menu: ipywidgets.Text()
        Widget containing the city selected by user
    
    Returns
    -------
    bbox: tuple
        The bounding box chosen by user
    """
    if (tab.selected_index == 0):
        bbox = [lonmax.value, latmax.value, lonmin.value, latmin.value]
    elif(tab.selected_index == 1):
        polygon, bbox, place_name = city_polygon_bbox(cities_menu.value)
        with out:
            print(place_name)
    elif (tab.selected_index == 2):
        bbox = tuple(map(float, raw_bbox_menu.value.split(',')))
    lonmax.value = bbox[0]
    latmax.value = bbox[1]
    lonmin.value = bbox[2]
    latmin.value = bbox[3]
    raw_bbox_menu.value = ','.join([str(elem) for elem in bbox])
    with out:
        print(f'BBOX = ({raw_bbox_menu.value})')
        clear_output(wait=True)
    return bbox


def get_collection(bbox):
    collection_widget = widgets.Dropdown(
        options=[('Sentinel2-L1C',('Sentinel2','L1C')),('Sentinel2-L2A',('Sentinel2','L2A')),
                 ('Sentinel1-GRD',('Sentinel1','GRD')),('Sentinel5P-L2',('Sentinel5P','L2'))],
        description='Collection',
    )
    button = widgets.Button(description = 'Validate')
    out = widgets.Output()
    display(collection_widget)
    display(button)
    display(out)
    
    def click_collection(b):
        with out:
            clear_output(wait=True)
            get_layer(collection_widget,bbox)
    button.on_click(click_collection)


def get_layer(collection_widget,bbox):
    (sattellite,collection) = collection_widget.value
    layer_widget = widgets.Dropdown(
        options=DICT_LAYER[sattellite + '-' + collection],
        description='Layer',
    )
    button = widgets.Button(description = 'Validate')
    out = widgets.Output()
    display(layer_widget)
    display(button)
    display(out)
    
    def click_layer(b):
        with out:
            clear_output(wait=True)
            get_param(collection_widget,layer_widget,bbox)
    button.on_click(click_layer)


def get_param(collection_widget,layer_widget,bbox):
    (satellite,_) = collection_widget.value
    date_dict={'Sentinel1':datetime.date(2018, 9, 1),'Sentinel2':datetime.date(2016,10,15),'Sentinel5P':datetime.date(2018, 9, 1)}
    start_date_widget = widgets.DatePicker(
        description='Starting Date',
        value = date_dict[satellite],
        disabled=False
    )
    stop_date_widget = widgets.DatePicker(
        description='Stopping Date',
        value = datetime.date.today() - datetime.timedelta(14),
        disabled=False
    )
    download_widget = widgets.Checkbox(
        value=False,
        description='Download Images',
        disabled=False,
        indent=True
    )
    output_name_widget = widgets.Text(
        value='output.gif',
        placeholder='Output Name',
        description='Output Name',
        disabled=False
    )
    title_widget = widgets.Text(
        value='',
        placeholder='Title to print on the GIF',
        description='Title',
        disabled=False
    )
    subtitle_widget = widgets.Text(
        value='',
        placeholder='Subtitle to print on the GIF',
        description='Subtitle',
        disabled=False
    )
    delta_days_widget = widgets.IntText(
        value=30,
        description='Time delta',
        disabled=False
    )
    height_widget = widgets.IntText(
        value=480,
        description='Height',
        disabled=False
    )
    width_widget = widgets.IntText(
        value=720,
        description='Width',
        disabled=False
    )
    duration_widget = widgets.IntText(
        value=5,
        description='GIF Duration (in seconds)',
        disabled=False
    )
    button_widget = widgets.Button(
        description='Generate GIF',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',
    )
    output_widget = widgets.Output(
    )
    output_gif = widgets.Output(
    )
    
    display(start_date_widget)
    display(stop_date_widget)
    display(download_widget)
    display(output_name_widget)
    display(title_widget)
    display(subtitle_widget)
    display(delta_days_widget)
    display(height_widget)
    display(width_widget)
    display(duration_widget)
    display(button_widget)
    display(output_widget)
    display(output_gif)

    def click_gif(b):
        with output_widget:
            generate_gif(bbox,collection_widget.value,layer_widget.value,start_date_widget.value,
                         stop_date_widget.value,download_widget.value,output_name_widget.value,
                         title_widget.value,subtitle_widget.value,delta_days_widget.value,
                         height_widget.value,width_widget.value,duration_widget.value)
    button_widget.on_click(click_gif)


# Display function, it searches all the GIF file in the /work directory and display the GIF you want
def display_gif():
    accepted_extensions = ["gif"]
    filenames = [fn for fn in os.listdir("../work") if fn.split(".")[-1] in accepted_extensions]
    file_widget = widgets.Dropdown(
         options= filenames,
         description='File to open',
    )
    button_file = widgets.Button(description = 'Display GIF')
    out_wid = widgets.Output()
    display(file_widget)
    display(button_file)
    display(out_wid)

    def click_file(b):
        with out_wid:
            clear_output(wait=True)
            display(HTML('<img src="{}">'.format('../work/' + file_widget.value)))
            
    button_file.on_click(click_file)