# -*- coding: utf-8 -*-
import json
import copy
import utils

class EvalService:
    def __init__(self, rules_config):
        self.rules_config = rules_config

    def eval_expressions_rules(self, params_json):
        #统一编码
        params_utf8 = params_json.encode('utf-8')
        expression_failure = []
        try:
            features = json.loads(params_utf8)
        except Exception as e:
            features = {}
            expression_failure.append('load_express_error')
        activity = features['activity']
        #获取expressions和rules
        expressions = self.rules_config.get(activity).get('expressions')
        rules = self.rules_config.get(activity).get('rules')
        context_tmp = copy.deepcopy(features)
        #运行expression，将key和运行结果保存
        for item in expressions:
            try:
                key = item['key']
                expr = item['expression']
                context_tmp[key] = eval(expr.encode('utf-8'), context_tmp)
                features[key] = context_tmp[key]
            except Exception as e:
                expression_failure.append('{key}:{expr} exception:{exception}'.format(key=key, expr=expr, exception=str(e)))
        features['expression_failure'] = expression_failure
        rule_failure = []
        production_policies = []
        production_describes = []
        dark_policies = []
        dark_describes = []
        test_policies = []
        policies = []
        marks = []
        for rule in rules:
            describe = rule.get('describe')
            mode = rule.get('mode')
            code = rule.get('code')
            expr = rule.get('rule')
            is_hit = False
            try:
                expr_res = eval(expr.encode('utf-8'), context_tmp)
                if type(expr_res) == bool:
                    is_hit = expr_res
            except Exception as e:
                rule_failure.append(str(rule))
            #分为production、dark和test三种状态，方便调试
            if is_hit:
                if mode == 'production':
                    production_policies.append(code)
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
        return json.dumps(features, ensure_ascii=False)
