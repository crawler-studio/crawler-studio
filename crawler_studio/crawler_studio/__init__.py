import logging
import os
import pymysql
from environs import Env

pymysql.install_as_MySQLdb()

logging.getLogger('pika').setLevel('ERROR')

