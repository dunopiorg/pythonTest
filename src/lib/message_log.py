import pymysql.cursors
import json
import logging
import logging.handlers
import config
from lib import query_loader


class MsgLog(object):
    HOST = config.DB_HOST
    USER = config.DB_USER
    PASSWORD = config.DB_PASSWORD
    DB = config.DB_NAME
    PORT = config.DB_PORT
    ql = query_loader.QueryLoader()
    # ql = query_loader.QueryLoader('../query_xml')

    @classmethod
    def insert_log(cls, msg_dict):
        conn = pymysql.connect(host=cls.HOST, port=cls.PORT, user=cls.USER,
                               password=cls.PASSWORD, db=cls.DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_log", "insert_log")
        query = query_format.format(**msg_dict)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)
            conn.commit()

        result = cursor.fetchall()

        return result

    @classmethod
    def get_count(cls, msg_info):
        conn = pymysql.connect(host=cls.HOST, port=cls.PORT, user=cls.USER,
                               password=cls.PASSWORD, db=cls.DB, charset='utf8mb4')

        query_format = cls.ql.get_query("query_log", "get_count")
        query = query_format.format(**msg_info)

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query)

        result = cursor.fetchall()

        return result


class MysqlHandler(logging.Handler):
    def __init__(self):
        self.HOST = config.DB_HOST
        self.USER = config.DB_USER
        self.PASSWORD = config.DB_PASSWORD
        self.DB = config.DB_NAME
        self.PORT = config.DB_PORT
        # ql = query_loader.QueryLoader()
        self.ql = query_loader.QueryLoader('../query_xml')
        logging.Handler.__init__(self, level=logging.NOTSET)

    def emit(self, record):
        conn = pymysql.connect(host=self.HOST, port=self.PORT, user=self.USER,
                               password=self.PASSWORD, db=self.DB, charset='utf8mb4')
        data = record.__dict__.copy()
        data.update(data['args'])
        query_format = self.ql.get_query("query_log", "insert_log")
        query = query_format.format(**data)

        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query)
        except Exception as ex:
            logging.error("Error: %s", ex)
    #todo : emit에서 record를 가져와서 나누자 - 바탕화면 이미지 참고

#if __name__ == "__main__":
    # logger = logging.getLogger('myloger')
    #
    # formatter = logging.Formatter('[%(levelname)s|%(filename)s|%(lineno)d] %(asctime)s > %(message)s')
    #
    # file_handler = logging.FileHandler('./test.log')
    # stream_handler = logging.StreamHandler()
    #
    # file_handler.setFormatter(formatter)
    # stream_handler.setFormatter(formatter)
    #
    # logger.addHandler(file_handler)
    # logger.addHandler(stream_handler)
    #
    # logger.setLevel(logging.DEBUG)
    # logger.debug("=========================================")
    # logger.info("test start")
    # logger.info("파일에다가 남겨봐요~")
    # logger.info("=========================================")
    # logger.debug("디버깅용 로그~~")
    # logger.info("도움이 되는 정보를 남겨요~")
    # logger.warning("주의해야되는곳!")
    # logger.error("에러!!!")
    # logger.critical("심각한 에러!!")
    # logger = logging.getLogger('myloger')
    # logger.addHandler(MysqlHandler())
    # d = {'tb': 'B', 'test': 'T', 'ok': 0}
    #
    # msg_logger = MsgLog()
    #
    # msg_logger.is_msg_exist()
