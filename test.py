import requests
import json


if __name__ == '__main__':
    #服务器请求
    url = "http://local:5000/my_eval"
    #请求内容
    data = {'activity': 'test', 'ua_cnt': 4}
    post_data = {'data': json.dumps(data)}
    a = requests.post(url=url, data=post_data)
    print(a.text)