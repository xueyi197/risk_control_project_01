from flask import Flask, request
import logging
import json

from engines import EvalService
from clickhouse_driver import Client
import datetime

# 全局配置
config = None
# 规则引擎
engine = None
# 配置上次拉取时间，初始化为当前时间减去10分钟，是为了保证第一次加载文件的时候满足更新条件
config_load_time = datetime.datetime.now() - datetime.timedelta(seconds=600)
# 配置规则引擎更新型号

client = Client(host='127.0.0.0', port='9000', user='default', password='***')

logging.basicConfig(
    format='[%(asctime)s]-[%(name)s]-[%(levelname)s]-[%(process)d]-[%(thread)d](%(filename)s:%(lineno)s): %('
           'message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# 设置日志输出级别为WARNING
logging.getLogger().setLevel(logging.WARNING)


# 使用Flask类创建一个app对象
# __name__ 代表当前的这个模块
# 1.以后出现bug，它可以帮助我们快速定位
# 2.对于寻找模板文件，有一个相对路径
app = Flask(__name__)


# 获取文章内容
@app.route('/hello')
def calc(article_id):
    return 'hello, I am engine'

# 获取规则配置
def get_config(name):
    with open(name) as f:
        s = f.read()
    return json.loads(s)

def g_config():
    global config, config_load_time, need_update
    # 计算上次加载到现在的时间
    gap = datetime.datetime.now() - config_load_time
    # 如果config为空，或者上次更新时间距现在不足一分钟，则直接返回
    if config and gap < datetime.timedelta(seconds=60):
        return config
    else:
    # 读取配置，并且更新时间，并且告诉规则引擎下次需要更新引擎
        config = get_config('test.json')
        config_load_time = datetime.datetime.now()
        need_update = True
    return config


def g_engine(config):
    global engine, need_update
    # 如果规则引擎存在，且不需要更新，则直接返回
    if engine and need_update == False:
        return engine
    else:
    # 更新规则引擎，并且把need_update置为False
        engine = EvalService(config)
        need_update = False
    return engine

# 规则引擎
@app.route('/my_eval', methods=['POST'])
def my_eval():
    global client
     # 获取POST请求中的data参数
    data = request.form['data']
    config = g_config()
    engine = g_engine(config)
    res = engine.eval_expressions_rules(data)
    str_res = str(res)
    logging.warning('res:{}'.format(str_res))
    sql = """
    insert into risk_control_log(res) VALUES('{}')
    """
    sql = sql.format(str_res)
    client.execute(sql)   
    return res

# 运行代码
if __name__ == '__main__':
    app.run(host='0.0.0.0')
