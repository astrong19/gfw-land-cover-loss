from hyp.marshmallow import Responder
from landcoverloss.schemas import ErrorSchema


class ErrorResponder(Responder):
    TYPE = 'errors'
    SERIALIZER = ErrorSchema
