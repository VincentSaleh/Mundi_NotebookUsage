#!/usr/bin/python
# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2018 Mundi Web Services
#
# Author : Patricia Segonds
#
# Contact email: patricia.segonds@atos.net
# =============================================================================

from owslib.wms  import WebMapService
from owslib.wmts import WebMapTileService
from owslib.wfs  import WebFeatureService
from owslib.wcs  import WebCoverageService
from owslib.csw  import CatalogueServiceWeb
from owslib.csw  import CswRecord

from owslib.util import openURL
from owslib.util import ResponseWrapper 

from owslib.util import OrderedDict

from math import ceil # upper round

import lxml.etree

    
### Mundi definitions

# ----------------
#    End points
# ----------------
# collection ids
# TODO : addition of other ids (from Landsat, Sentinel3, ...)
mundi_id = {'Sentinel1': "88b68ca0-1f84-4286-8359-d3f480771de5", \
            'Sentinel2': "d275ef59-3f26-4466-9a60-ff837e572144"}

# web services
mundi_services = {'wms': "http://shservices.mundiwebservices.com/ogc/wms/", \
                  'wmts': "http://shservices.mundiwebservices.com/ogc/wmts/", \
                  'wfs': "http://shservices.mundiwebservices.com/ogc/wfs/", \
                  'wcs': "http://shservices.mundiwebservices.com/ogc/wcs/"}

# WAITING : up information should be all get from csw discovery


# Used namespaces
mundi_nsmap = {'atom'    : "http://www.w3.org/2005/Atom", \
               'csw'     : "http://www.opengis.net/cat/csw/2.0.2", \
               'dc'      : "http://purl.org/dc/elements/1.1/", \
               'dct'     : "http://purl.org/dc/terms/", \
               'DIAS'    : "http://tas/DIAS", \
               'eo'      : "http://a9.com/-/spec/opensearch/extensions/eo/1.0/", \
               'geo'     : "http://a9.com/-/opensearch/extensions/geo/1.0/", \
               'georss'  : "http://www.georss.org/georss", \
               'media'   : "http://search.yahoo.com/mrss/", \
               'os'      : "http://a9.com/-/spec/opensearch/1.1/", \
               'ows'     : "http://www.opengis.net/ows" , \
               'param'   : "http://a9.com/-/spec/opensearch/extensions/parameters/1.0/", \
               'referrer': "http://www.opensearch.org/Specifications/OpenSearch/Extensions/Referrer/1.0", \
               'sru'     : "http://a9.com/-/opensearch/extensions/sru/2.0/", \
               'time'    : "http://a9.com/-/opensearch/extensions/time/1.0/", \
               'xmlns'   : "http://www.w3.org/2001/XMLSchema", \
               'xsi'     : "http://www.w3.org/2001/XMLSchema-instance"}



# ----------------------------------------------------------------
#  mundi catalogue class
# ----------------------------------------------------------------
class mundiCatalogue():
       
    # opensearchDescription
    osdd = ""
    # csw entry point
    csw_end_point = "https://mundiwebservices.com/acdc/catalog/proxy/search/global/csw"
    
    # lis of mundiCollection object
    _collections = []
    
    def __init__(self):
        """Constructor"""
        osdd_file = "https://mundiwebservices.com/acdc/catalog/proxy/search/collections/opensearch/description.xml"
        self.osdd = opensearchDescription(osdd_file)
        # getting 'platforms' from osdd file
        platforms = self.osdd.findall('.//param:Parameter[@name="platform"]/param:Option')
        mundi_platforms = sorted(set([p.get('value') for p in platforms]))
        for p in mundi_platforms:
            self._collections.append(mundiCollection(p))
    
    def getCollections(self):
        return self._collections
    
    def getCollection(self, name):
        mc = ""
        for c in self._collections:
            if c.name == name:
                mc = c
        if mc == "":
            raise mundiException(UNAVAILABLE_COLLECTION)
        return mc
    
    # --- CSW web service ---
    def mundi_csw(self, version = "2.0.2"):
        if version in ["2.0.2"]:
            csw = mundiCatalogueServiceWeb(self.csw_end_point, version)
        else:
            raise mundiException(UNSUPPORTED_SERVICE)         
        return csw    



# ----------------------------------------------------------------
#  mundi catalogue web service class
# ----------------------------------------------------------------
class mundiCatalogueServiceWeb(CatalogueServiceWeb):
    
    def __init__(self, url, version):
        """Constructor"""
        super().__init__(url, version)
        
    # get metadata list (name:value) as dictionnary
    # As indicated in 'describerecord' from 'owslib/csw' here is done following:
    # TODO: process the XML Schema (you're on your own for now with self.response)
    def mundidescriberecord(self):
            
        # getting root node from 'DescribeRecord' request
        self.describerecord(typename='csw:Record', format='application/xml')
        root = lxml.etree.fromstring(self.response)
        
        # getting node containing all elements 
        # (i.e. '<complexType name="RecordType" final="#all">')
        node = root.find('.//csw:SchemaComponent/xmlns:schema/xmlns:complexType[@name="RecordType"]', namespaces=mundi_nsmap)
        nodes = node.findall('.//*xmlns:element', namespaces=mundi_nsmap)

        elems = {}
        for n in nodes:
            d = n.find(".//*xmlns:documentation", namespaces=mundi_nsmap)
            if d is not None:
                elems[n.get('ref')] = d.text.replace("\n","")   
        return elems

    # 'GetRecords' returning all request records from on all pages
    def mundigetrecords2(self, xml):
        # removing unrelevant information from given payload
        payload = xml.strip()
            
        # all 'csw:Record' dictionnary from 'GetRecords' request pages
        all_records = OrderedDict()
        
        # getting first page (i.e. 'page0')
        self.getrecords2(xml=payload)
        all_records.update(self.records)
        page0 = lxml.etree.fromstring(self.response)
        
        sr_node = page0.find('csw:SearchResults', namespaces=mundi_nsmap)
        nb_total    = int(sr_node.get("numberOfRecordsMatched"))
        nb_set      = int(sr_node.get("numberOfRecordsReturned"))
        next_record = int(sr_node.get("nextRecord"))
        
        # calculation of page number
        if (nb_total == 0):
            nbPages = 1
        else:
            nbPages = ceil(nb_total/nb_set)
        
        # getting other/next pages (i.e. 'pageN')
        i = 1
        while (i < nbPages):
            # modifying payload with new start position
            node_p = lxml.etree.fromstring(payload)
            node_p.set('startPosition', str(next_record))
            payload = lxml.etree.tostring(node_p, pretty_print=True) 
            self.getrecords2(xml=payload)
            pageN = lxml.etree.fromstring(self.response)
            sr_node = pageN.find('csw:SearchResults', namespaces=mundi_nsmap)
            next_record = int(sr_node.get("nextRecord"))
            all_records.update(self.records)
            # go next page
            i += 1
        self.records = all_records

    # get volume of records of a 'GetRecords' request (i.e. 'productDatapackSize' value sum)
    # expressed in TB
    def mundigetvolrecords2(self, xml):
        self.mundigetrecords2(xml=xml)
        volume = 0

        # sum of '<DIAS:productDatapackSize>'
        for name, cswRecord in self.records.items():
            node = lxml.etree.fromstring(cswRecord.xml)
            node_size = node.find("DIAS:productDatapackSize", namespaces=mundi_nsmap)
            volume += float(node_size.text) / 1000 / 1000 / 1000
        volume = round(volume, 2)
        return volume

    # get number of records of a 'GetRecords' request (i.e. 'numberOfRecordsMatched' value)
    def mundigetnbrecords2(self, xml):
        # removing unrelevant information from given payload
        payload = xml.strip()
        
        # getting only first page (i.e. 'page0')
        self.getrecords2(xml=payload)
        page0 = lxml.etree.fromstring(self.response)
        
        # 'numberOfRecordsMatched'
        sr_node = page0.find('csw:SearchResults', namespaces=mundi_nsmap)
        nb = int(sr_node.get("numberOfRecordsMatched"))
        return nb
        
      
        
# ----------------------------------------------------------------
#  mundi collection class
# ----------------------------------------------------------------
class mundiCollection:
    
    # collection name
    name = ""
    # opensearchDescription
    osdd = ""
    # end point of 'csw' web service for current collection
    csw_end_point  = ""
    
    def __init__(self, name):
        """Constructor"""
        self.name = name
        osdd_file = "https://mundiwebservices.com/acdc/catalog/proxy/search/{mundi_collection}/opensearch/description.xml".replace('{mundi_collection}', self.name)
        self.osdd = opensearchDescription(osdd_file)
        self.csw_end_point = "https://mundiwebservices.com/acdc/catalog/proxy/search/{mundi_collection}/csw?service=CSW".replace('{mundi_collection}', self.name)
        
    # get web service endpoint url
    def _serviceEndPoint(self, service):
        if (self.name in mundi_id):
            ep = mundi_services[service] + mundi_id[self.name]
        else:
            raise mundiException(UNAVAILABLE_COLLECTION_SERVICE)
        return ep
    
    # get 'productType' nodes
    def productTypes(self):
        list = self.osdd.find('.//param:Parameter[@name="productType"]')
        if list is None:
            list = []
        return list

    # get 'processingLevel' nodes
    def processingLevels(self):
        list = self.osdd.find('.//param:Parameter[@name="processingLevel"]')
        if list is None:
            list = []
        return list

    # --- CSW web service ---
    def mundi_csw(self, version = "2.0.2"):
        if version in ["2.0.2"]:
            csw = mundiCatalogueServiceWeb(self.csw_end_point, version)
        else:
            raise mundiException(UNSUPPORTED_SERVICE)         
        return csw    
    
    # --- WMS web service ---
    def mundi_wms(self, version = "1.3.0"):
        if version in ["1.3.0", "1.1.1"]:
            wms = WebMapService(self._serviceEndPoint('wms'), version)
        else:
            raise mundiException(UNSUPPORTED_SERVICE)         
        return wms

    # --- WMTS web service ---
    def mundi_wmts(self, version="1.0.0"):
        if version in ["1.0.0"]:
            wmts = WebMapTileService(self._serviceEndPoint('wmts'), version)
        else:
            raise mundiException(UNSUPPORTED_SERVICE)         
        return wmts

    # --- WFS web service ---
    def mundi_wfs(self, version="2.0.0"):
        if version in ["2.0.0"]:
            wfs = WebFeatureService(self._serviceEndPoint('wfs'), version)
        else:
            raise mundiException(UNSUPPORTED_SERVICE)         
        return wfs

    #  --- WCS web service ---
    # Supported versions are: 1.0.0, 1.1.0, 1.1.1 and 1.1.2
    def mundi_wcs(self, version="1.0.0"):
        if version in ["1.0.0", "1.1.0", "1.1.1", "1.1.2"]:
            wcs = WebCoverageService(self._serviceEndPoint('wcs'), version)
        else:
            raise mundiException(UNSUPPORTED_SERVICE)         
        return wcs 



# ----------------------------------------------------------------
#  methods on cswRecord
# ----------------------------------------------------------------
def findnode(cswRecord, match):    
    root_node  = lxml.etree.fromstring(cswRecord.xml)
    match_node = root_node.find(match, namespaces=mundi_nsmap)
    return match_node



# ----------------------------------------------------------------
#  methods on ResponseWrapper
# ----------------------------------------------------------------
def _findentries(ResponseWrapper):
    root_node  = lxml.etree.fromstring(ResponseWrapper.read())
    entries = root_node.findall("atom:entry", namespaces=mundi_nsmap)
    return entries

def findentries(ResponseWrapper_list):
    entries = []
    for rw in ResponseWrapper_list:
        el = _findentries(rw)
        for entry in el:
            entries.append(entry)
    return entries


    
# ----------------------------------------------------------------
#  opensearch description file class
# ----------------------------------------------------------------
class opensearchDescription:
   
    # 'description.xml' file url
    desc_file = ""
    # osdd document root node
    root = ""
    
    def __init__(self, osdd):
        page = openURL(osdd, method='Get')
        response_wrapper = page.read()
        self.root = lxml.etree.fromstring(response_wrapper)

    # surcharge to use namespaces
    def xpath(self, query):
        return self.root.xpath(query, namespaces=mundi_nsmap)
    
    # surcharge to use namespaces
    def find(self, query):
        return self.root.find(query, namespaces=mundi_nsmap)

    # surcharge to use namespaces
    def findall(self, query):
        return self.root.findall(query, namespaces=mundi_nsmap)


    
# ----------------------------------------------------------------
#  opensearch methods
# ----------------------------------------------------------------
# get list of ResponseWrapper from a given open search request
def mundiopenURL2(col="", query="", data=None, method='Get', cookies=None, username=None, password=None, timeout=30, headers=None, verify=True, cert=None):
            
    if col != "":
        os_query = "https://mundiwebservices.com/acdc/catalog/proxy/search/{mundi_collection}/opensearch?".replace('{mundi_collection}', col.name) + query
    else:
        os_query = "https://mundiwebservices.com/acdc/catalog/proxy/search/global/opensearch?" + query
    
    response_wrappers = []
    
    # getting first page (i.e. 'page0')
    page0 = openURL(os_query, data, method, cookies, username, password, timeout, headers, verify, cert)
    response_wrapper_0 = page0.read()
    rw0_node = lxml.etree.fromstring(response_wrapper_0)
    response_wrappers.append(page0)
    
    nb_total    = int(rw0_node.xpath('os:totalResults', namespaces=mundi_nsmap)[0].text)
    nb_set      = int(rw0_node.xpath('os:itemsPerPage', namespaces=mundi_nsmap)[0].text)
    start_index = int(rw0_node.xpath('os:startIndex', namespaces=mundi_nsmap)[0].text)
    
    next_record = start_index + nb_set
    
    # calculation of page number
    if (nb_total == 0):
        nbPages = 1
    else:
        nbPages = ceil(nb_total/nb_set)
    
    # getting other/next pages (i.e. 'pageN')
    i = 1
    while (i < nbPages):
        # modifying payload with new start position
        os_query_N = os_query + "&startIndex=" + str(next_record)
        page_N = openURL(os_query_N, data, method, cookies, username, password, timeout, headers, verify, cert)
        response_wrappers.append(page_N)
    
        next_record += nb_set
        # go next page
        i += 1
    
    return response_wrappers


# get number of results from a given open search request
def mundinbopenURL2(col="", query="", data=None, method='Get', cookies=None, username=None, password=None, timeout=30, headers=None, verify=True, cert=None):
            
    if col != "":
        os_query = "https://mundiwebservices.com/acdc/catalog/proxy/search/{mundi_collection}/opensearch?".replace('{mundi_collection}', col.name) + query
    else:
        os_query = "https://mundiwebservices.com/acdc/catalog/proxy/search/global/opensearch?" + query
    
    # getting first page (i.e. 'page0')
    page0 = openURL(os_query, data, method, cookies, username, password, timeout, headers, verify, cert)
    response_wrapper_0 = page0.read()
    rw0_node = lxml.etree.fromstring(response_wrapper_0)
    
    nb = int(rw0_node.xpath('os:totalResults', namespaces=mundi_nsmap)[0].text)
    
    return nb


        
# ----------------------------------------------------------------
#  EXCEPTIONS MANAGEMENT - mundi specific exceptions declaration
# ----------------------------------------------------------------
    
# mundi error messages
UNSUPPORTED_SERVICE            = "Unsupported web service version requested."
UNAVAILABLE_COLLECTION         = "Unavailable collection."
UNAVAILABLE_COLLECTION_SERVICE = "Unavailable service on collection."

# mundi specific exceptions
class mundiException(Exception):
    """Exception raised for specific Mundi errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
      
        
        
# ----------------------------------------------------------------
#  toolbox - bbox
# ----------------------------------------------------------------
# get optimized witdh for a given heigth regarding a known bbox
def width(bbox, height):
    x1, y1, x2, y2 = bbox
    width = int(height * (x2-x1) / (y2-y1))
    return width

# get optimized height for a given width regarding a known bbox
def height(bbox, width):
    x1, y1, x2, y2 = bbox
    height = int(width * (y2-y1) / (x2-x1))
    return height
