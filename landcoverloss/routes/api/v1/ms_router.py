import os
import json
import csv
import StringIO
import logging
import urllib

from flask import jsonify, request, Response, stream_with_context
import requests

from . import endpoints
from landcoverloss.responders import ErrorResponder
from landcoverloss.utils.http import request_to_microservice

#next steps
#how does vizz grab the geoetry?
#need to send the geostore id to the microservice and get back the geojson
#/geostore/id
#example: https://github.com/resource-watch/adapter-earth-engine/blob/master/adapterearthengine/utils/http.py
#make geometry an argument... for geostore you get a hash... send it to the geostore, get the geometry, transform geostore to esri json

#Get geojson from geostore
@endpoints.route('/landcoverloss', methods=['GET'])
def get_geostore():
    logging.info('requesting geojson from geostore')

    geo = request.args.get('geometry', None)
    logging.info('geo specified: %s' %(geo))

    if not geo:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'geostore ID should be included'
            }]
        }), 400

    try:
        geostore = 'http://production-api.globalforestwatch.org/geostore/{0}'.format(geo)

    except Error:
        return jsonify({'errors': [{
            'status': '404',
            'detail': 'endpoint not found'
            }]
        }), 404

    geo_resp = requests.get(url=geostore)
    geojson = geo_resp.json()
    r = {'geom': geojson['data']['attributes']['geojson']['features'][0]['geometry']}

    return jsonify(r), 200
    get_esri_json()

@endpoints.route('/geojson-ms-example/to-esri', methods=['GET'])
def get_esri_json():

    logging.info('converting geojson to esri json')

    geo = get_geostore()

    staging_token = os.getenv('CT_Token')

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(staging_token)}

    # payload =  {'geom': geo}
    payload = geo

    try:
        r = requests.post("localhost:9000/geojson-ms-example/to-esri", headers=headers, json=payload)
        esri_json = r.json()
        rings = response['rings']
        logging.info("esri json: %s" %(esri_json))
        return jsonify(rings), 200
        logging.info("esri json created")
        make_request()

    except Error:
         return jsonify({'errors': [{
             'status': '500',
             'title': 'Service unavailable'
             }]
         }), 500

@endpoints.route('/landcoverloss', methods=['POST'])
def make_request():
    """Make request to image service"""
    logging.info('pinging image service')

    shape = 'esriGeometryPolygon'

    geom = {
            'type': 'Polygon',
            'rings': get_esri_json()
    }

    # direct_geometry = urllib.unquote(geo).decode()

    #geometry = '{"type":"Polygon","rings":[[[-52.108154296875,-8.537565350804018],[-52.437744140625,-9.156332560046778],[-52.020263671875,-9.329831355689176],[-51.690673828125,-8.733077421211563],[-52.108154296875,-8.537565350804018]]]}'

    mosaic_rule = '{"mosaicMethod":"esriMosaicLockRaster","lockRasterIds":[1],"ascending":true,"mosaicOperation":"MT_FIRST"}'

    rendering_rule = '{"rasterFunction":"Arithmetic","rasterFunctionArguments":{"Raster":{"rasterFunction":"Remap","rasterFunctionArguments":{"InputRanges":[0,30,30,101],"OutputValues":[0,1],"Raster":"$2","AllowUnmatched":false}},"Raster2":{"rasterFunction":"Arithmetic","rasterFunctionArguments":{"Raster":{"rasterFunction":"Arithmetic","rasterFunctionArguments":{"Raster":{"rasterFunction":"Remap","rasterFunctionArguments":{"InputRanges":[1,16],"OutputValues":[16],"Raster":"$1","AllowUnmatched":false}},"Raster2":"$1","Operation":3}},"Raster2":"$3","Operation":1},"outputPixelType":"U8"},"Operation":3}}'

    url = 'http://gis-gfw.wri.org/arcgis/rest/services/image_services/tree_cover_loss_year_wgs84/ImageServer/computeHistograms?geometry={0}&geometryType={1}&renderingRule={2}&f=json'.format(geom, shape, mosaic_rule)

    resp = requests.get(url=url)
    data = resp.json()

    return jsonify({'data': data}), 200
