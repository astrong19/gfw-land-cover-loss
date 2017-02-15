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
def test():
    """Test service"""
    logging.info('running test')
    return jsonify({'data': 'it worked!'}), 200
