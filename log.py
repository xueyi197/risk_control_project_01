import logging


logging.basicConfig(
    format='[%(asctime)s]-[%(name)s]-[%(levelname)s]-[%(process)d]-[%(thread)d](%(filename)s:%(lineno)s): %('
           'message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# 设置日志输出级别为WARNING
logging.getLogger().setLevel(logging.WARNING)