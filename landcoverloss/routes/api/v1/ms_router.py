import os
import json
import csv
import StringIO
import logging

from flask import jsonify, request, Response, stream_with_context
import requests

from . import endpoints
from landcoverloss.responders import ErrorResponder
from landcoverloss.utils.http import request_to_microservice


@endpoints.route('/landcoverloss', methods=['GET'])
def make_request():
    """Make request to image service"""
    logging.info('pinging image service')

    shape = 'esriGeometryPolygon'

    geometry = '{"type":"Polygon","rings":[[[-52.108154296875,-8.537565350804018],[-52.437744140625,-9.156332560046778],[-52.020263671875,-9.329831355689176],[-51.690673828125,-8.733077421211563],[-52.108154296875,-8.537565350804018]]]}'

    mosaic_rule = '{"mosaicMethod":"esriMosaicLockRaster","lockRasterIds":[1],"ascending":true,"mosaicOperation":"MT_FIRST"}'

    #how does vizz grab the geoetry?

    url = 'http://gis-gfw.wri.org/arcgis/rest/services/image_services/tree_cover_loss_year_wgs84/ImageServer/computeHistograms?geometry={0}&geometryType={1}&mosaicRule={2}&f=json'.format(geometry, shape, mosaic_rule)

    resp = requests.get(url=url)
    data = resp.json()

    return jsonify({'data': data}), 200
