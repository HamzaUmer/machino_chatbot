from flask import Blueprint
from flask_restx import Api
from apis.machino_chatbot import api as machino_qna

blueprint = Blueprint('api', __name__, url_prefix='/')
api = Api(blueprint,
    title='Machino Chatbot',
    version='1.0',
    description='Machino Chatbot',
)


api.add_namespace(machino_qna)
