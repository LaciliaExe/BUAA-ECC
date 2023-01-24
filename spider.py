# -!- coding: utf-8 -!-
import re, requests
from fake_useragent import UserAgent #随机生成一个user-agent

def Spider(id_light, id_aircond):

    headers = {'User-Agent':UserAgent().random}

    url_light = 'https://shsd.buaa.edu.cn/PubBuaa?id={}'.format(int(id_light))
    html_light = requests.get(url=url_light, headers=headers).content.decode("utf-8")
    res_light = float(re.findall('<tspan x="100" y="114">.*?</tspan>',html_light)[0]\
        .replace('<tspan x="100" y="114">','').replace('</tspan>',''))


    url_aircond = 'https://shsd.buaa.edu.cn/PubBuaa?id={}'.format(int(id_aircond))
    html_aircond = requests.get(url=url_aircond, headers=headers).content.decode("utf-8")
    res_aircond = float(re.findall('<tspan x="100" y="114">.*?</tspan>',html_aircond)[0]\
        .replace('<tspan x="100" y="114">','').replace('</tspan>',''))

    return [res_light, res_aircond]


