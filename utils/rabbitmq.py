# coding:utf-8
import datetime
import json
from crawler_studio_be.settings import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, UPLOAD_BUNDLE_KEY_EXCHANGE, UPLOAD_BUNDLE_KEY_QUEUE_NAME
import pika
import logging


logger = logging.getLogger(__name__)


class RabbitMQ2(object):
    """ RabbitMQ辅助类 https://pika.readthedocs.io/en/latest/index.html """

    __slots__ = ('_host', '_port', '_username', '_password', '_connection', '_channel', '_errors', '_consumer_dict')

    class ContentType(object):
        TEXT = 'text/plain'
        JSON = 'application/json'

    def __init__(self, host=RABBITMQ_HOST, port=RABBITMQ_PORT, username=RABBITMQ_USER, password=RABBITMQ_PASSWORD):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._connection = self.create_connection()
        self._channel = self.create_channel(self._connection)
        self._errors = set()
        self._consumer_dict = {}
        logger.info(f'实例化Rabbitmq %(username)s:%(password)s@%(host)s:%(port)s' % locals())

    def create_connection(self):
        credentials = pika.PlainCredentials(self._username, self._password)
        parameters = pika.ConnectionParameters(
            host=self._host,
            port=self._port,
            virtual_host='/',
            credentials=credentials,
            heartbeat=0
        )
        return pika.BlockingConnection(parameters)

    @staticmethod
    def create_channel(connection):
        return connection.channel()

    def get_default_properties(self):
        basic_properties = pika.BasicProperties()
        basic_properties.delivery_mode = 2
        basic_properties.content_type = self.ContentType.TEXT
        basic_properties.content_encoding = 'utf-8'
        return basic_properties

    def declare_queue(self, name):
        # passive (bool) – Only check to see if the queue exists
        """新建队列名"""
        self._channel.queue_declare(queue=name)

    def send(self, routing_key, data, properties=None, exchange=''):
        """
        :return:
        """
        try:
            basic_properties = self.get_default_properties()
            if properties and isinstance(properties, dict):
                for (key, value) in properties.items():
                    setattr(basic_properties, key, value)
            data_dumps = json.dumps(data, ensure_ascii=False).encode('utf8')
            if routing_key == UPLOAD_BUNDLE_KEY_QUEUE_NAME:
                exchange = UPLOAD_BUNDLE_KEY_EXCHANGE
            rs = self._channel.basic_publish(exchange=exchange, routing_key=routing_key, body=data_dumps, properties=basic_properties)
            logger.info(f'发送msg到{data}, {rs}')
        except Exception as e:
            self.reconnect(e)
            logger.error('queue func[send], routing_key=%s, data=%s, error: %s' % (routing_key, data, e))

    def get(self, name, ack=True, need_method=False):
        try:
            method, properties, data = self._channel.basic_get(queue=name, auto_ack=ack)
            if need_method:
                return method, data
            else:
                return data
        except Exception as e:
            self.reconnect(e)
            logger.error('queue func[get] error: %s' % e)

    def next_msg(self, queue_name, no_ack=True, need_method=False):
        try:
            consume = self._consumer_dict.get(queue_name)
            if not consume:
                consume = self._channel.consume(queue=queue_name, no_ack=no_ack)
                self._consumer_dict[queue_name] = consume
            for method, props, body in consume:
                if need_method:
                    yield method, body
                else:
                    yield body
        except Exception as e:
            self.reconnect(e)
            logger.error('queue func[get] error: %s' % e)

    def reconnect(self, e):
        self._errors.add(e)
        if len(self._errors) > 5:
            self._connection.close()
            self._connection = self.create_connection()
            self._channel = self.create_channel(self._connection)

    # def __del__(self):
    #     try:
    #         self._channel.cancel()
    #         self._channel.close()
    #         self._connection.close()
    #     except:
    #         pass

    def send_crawl_result(self, task_id, source_id, parent_id, run_ip, inst_id, success, err_code, err_msg, data_cnt):
        crawl_result = {
            'taskId': task_id,
            'sourceId': source_id,
            'parentId': parent_id,
            'runIp': run_ip,
            'instId': inst_id,
            'success': success,
            'errMsg': err_msg,
            'dataCnt': data_cnt,
            'endTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'err_code': err_code,
        }
        self.send('task_ret', crawl_result)


if __name__ == '__main__':
    rs = RabbitMQ2().get('news_twitter')
    print(rs)
