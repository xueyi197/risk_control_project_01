import requests
import json


if __name__ == '__main__':

    url = "***"

    data = {'activity': 'test', 'ua_cnt': 4}
    post_data = {'data': json.dumps(data)}

    a = requests.post(url=url, data=post_data)

    print(a.text)
    
