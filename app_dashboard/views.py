import re

from django.shortcuts import render

# Create your views here.
import pytz
from dateutil import parser
import time
import datetime
from django.http import HttpResponse, JsonResponse
from app_docs.models import Docs, DocsType
from django.http import HttpRequest
from elasticsearch import Elasticsearch
from crawler_studio_be.settings import ES_SERVER, ES_LOG_INDEX


def rabbitmq_monitor(request):
    pass


