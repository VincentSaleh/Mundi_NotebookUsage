# Mundi_NotebookUsage
Mundi library and use case of how-to use the platform in Jupyter Notebook.

# ------------------------------------------------------------------------------------------
#
#                            Welcome to Mundi Jupyter Notebook
#
# ------------------------------------------------------------------------------------------

#  /!\ Note that:
#          - your session will stop after a few minutes of inactivity,
#          - only elements in 'work' directory can be saved.

- Folders content:
'/lib/'    : Mundi library. It is Read Only.
             Based on 'OWSLib' https://geopython.github.io/OWSLib/: Python package compliant 
             with Open Geospatial Consortium (OGC) web service (hence OWS) interface standards, 
             and their related content models.

'/public/' : Contains Notebook examples. It is Read and Executable Only.      

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

'/work/'   : Personnal folder that will persist through Jupyter Notebook sessions. 
             Store anything you want to keep in that folder.


- Installed packages:
Use 'pip list' shell command to list all installed packages & version.
Specific ones:

            - -------------------------------------------------------------------------------------------------------------
            | Package name            | Description                                        | www                          |
            - -------------------------------------------------------------------------------------------------------------
            | gdal                    | Geospatial Data Abstraction library                | https://www.gdal.org/        |  
            | matplotlib              | Python 2D plotting library                         | https://matplotlib.org/      | 
            | NumPy                   | Base N-dimensional array package                   | http://www.numpy.org/        |        
            | pandas                  | Python Data structures & analysis library          | https://pandas.pydata.org/   | 
            | s3cmd                   | Command line tool for managing Amazon S3           | https://s3tools.org/s3cmd    |       
            - -------------------------------------------------------------------------------------------------------------
            
To install additional package a notebook cell like this can be included:
! pip install <package_name>
The notebook environment also supports opening a terminal, in which this command can be executed as well. 


- Clipboard usage:
Dot   + Tab                  : completion in notebook
MAJ   + Insert               : paste text from clipboard
Shift + <right_mouse_button> : access to clipboard


- Webography:
Bounding box finder : http://bboxfinder.com


