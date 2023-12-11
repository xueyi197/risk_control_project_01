# -*- coding: utf-8 -*-

import json
import copy
import redis
from redis import StrictRedis
from log import logging


class EvalService:
    def __init__(self, rules_config):
        self.rules_config = rules_config
        self.my_redis = StrictRedis(host='redis.com', port=26332, decode_responses=True, password='***')

    
    #读取并运行规则
    def eval_expressions_rules(self, params_json):
        #编码为utf-8
        params_utf8 = params_json.encode('utf-8')
        expression_failure = []
        counter_failure = []
        #将json读取为字典
        try:
            features = json.loads(params_utf8)
        except Exception as e:
            features = {}
            expression_failure.append('load_express_error')
        activity = features['activity']
        counter_read = self.rules_config.get(activity).get('counter_read')
        expressions = self.rules_config.get(activity).get('expressions')
        rules = self.rules_config.get(activity).get('rules')
        context_tmp = copy.deepcopy(features)
        #获取counter_read中的数据，并根据my_type来运行
        for counter in counter_read:
            try:
                key = counter.get('key')
                my_type = counter.get('type')
                redis_key = counter.get('redis_key')
                if counter.get('redis_key2') != None:
                    redis_key2 = counter.get('redis_key2')
                #访问次数
                if my_type == 'redis_cnt':
                    context_tmp[key] = int(self.my_redis.incr(eval(redis_key.encode('utf-8'), context_tmp)))
                #添加set数据
                elif my_type == 'redis_number':
                    context_tmp[key] = self.my_redis.sadd(eval(redis_key.encode('utf-8'), context_tmp),eval(redis_key2.encode('utf-8'), context_tmp))
                #返回去重元素
                elif my_type == 'quchongshu':
                    context_tmp[key] = len(self.my_redis.smembers(eval(redis_key.encode('utf-8'), context_tmp)))
                #添加string数据
                elif my_type == 'set_redis':
                    context_tmp[key] = self.my_redis.set(eval(redis_key.encode('utf-8'), context_tmp),eval(redis_key2.encode('utf-8'), context_tmp))
                #获取string数据
                elif my_type == 'get_redis':
                    context_tmp[key] = self.my_redis.get(eval(redis_key.encode('utf-8'), context_tmp))
                features[key] = context_tmp[key]
            except Exception as e:
                logging.warning(str(e))
                counter_failure.append('{key}:{my_type} '.format(key=key, my_type=my_type))
        features['counter_failure'] = counter_failure
        #获取expressions的key和expression，并且运行
        for item in expressions:
            try:
                key = item['key']
                expr = item['expression']
                context_tmp[key] = eval(expr.encode('utf-8'), context_tmp)
                features[key] = context_tmp[key]
            except Exception as e:
                logging.warning(str(e))
                expression_failure.append('{key}:{expr} '.format(key=key, expr=expr))
        features['expression_failure'] = expression_failure
        rule_failure = []
        production_policies = []
        production_describes = []
        dark_policies = []
        dark_describes = []
        test_policies = []
        policies = []
        marks = []
        risk_rate = []
        #获取rules
        for rule in rules:
            describe = rule.get('describe')
            mode = rule.get('mode')
            code = rule.get('code')
            expr = rule.get('rule')
            risk = rule.get('risk_rate')
            is_hit = False
            try:
                expr_res = eval(expr.encode('utf-8'), context_tmp)
                if type(expr_res) == bool:
                    is_hit = expr_res
            except Exception as e:
                logging.warning(str(e))
                rule_failure.append(str(rule))
            #分为production、dark和test三种模式，方便调试
            if is_hit:
                if mode == 'production':
                    production_policies.append(code)
                    risk_rate.append(risk)
                    production_describes.append(str(code) + ':' + str(describe))
                    marks.append('production:' + describe)
                elif mode == 'dark':
                    dark_policies.append(code)
                    dark_describes.append(str(code) + ':' + str(describe))
                    marks.append('dark:' + describe)
                elif mode == 'test':
                    test_policies.append(code)
                policies.append(code)
        features['rule_failure'] = rule_failure
        features['production_policies'] = production_policies
        features['production_describes'] = production_describes
        features['dark_policies'] = dark_policies
        features['dark_describes'] = dark_describes
        features['test_policies'] = test_policies
        features['policies'] = policies
        features['marks'] = marks
        features['risk_rate'] = risk_rate
        return json.dumps(features, ensure_ascii=False)