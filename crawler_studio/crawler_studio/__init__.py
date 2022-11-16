import logging
import os
import pymysql

pymysql.install_as_MySQLdb()

logging.getLogger('pika').setLevel('ERROR')

