import logging
import os
import pymysql
from environs import Env

pymysql.install_as_MySQLdb()

logging.getLogger('pika').setLevel('ERROR')


env = Env()
assert os.getenv("ENV", "dev") in ('dev', 'test', 'prod')
env.read_env(f'.env.{os.getenv("ENV", "dev")}')

