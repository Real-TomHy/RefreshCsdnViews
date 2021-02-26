# -*- coding:UTF-8 -*-

from lxml import html
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent

import re
import urllib.request
import urllib.parse

firefoxHead = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
IPRegular = r"(([1-9]?\d|1\d{2}|2[0-4]\d|25[0-5]).){3}([1-9]?\d|1\d{2}|2[0-4]\d|25[0-5])"
host = "https://blog.csdn.net"
url = "https://blog.csdn.net/lovely_yoshino/article/details/{}"
codes = ["106651719", "106533059", "107508976", "106658304", "106594490", "106242605"]


def get_user_agent(num):
    """
    生成不同的 user-agent
    :param num: 生成个数
    :return: list
    """
    ua = FakeUserAgent()
    user_agent = []
    for i in range(num):
        user_agent.append({'User-Agent': ua.random})
    return user_agent


def get_proxy(pages, ua_num, target_url):
    """
    爬取代理数据，清洗整合
    :param pages: 需要爬取页数
    :param ua_num: 需要user-agent个数
    :param target_url: 爬虫的目标地址，作为验证代理池ip的有效性
    :return: list
    """
    headers = get_user_agent(ua_num)  # 请求头
    proxy_list = []  # 最后需入库保存的代理池数据
    try:
        for num in range(0, pages):
            print('Start：第 %d 页请求' % (num + 1))
            # 请求路径
            url = 'https://www.kuaidaili.com/free/inha/' + str(num + 1) + '/'

            # 随机延时（randint生成的随机数n: a <= n <= b ；random产生 0 到 1 之间的随机浮点数）
            time.sleep(random.randint(1, 2) + random.random())
            header_i = random.randint(0, len(headers) - 1)  # 随机获取1个请求头

            # BeautifulSoup 解析
            html = requests.get(url, headers=headers[header_i])
            soup = BeautifulSoup(html.text, 'lxml')

            # CSS 选择器
            ip = soup.select("td[data-title='IP']")
            port = soup.select("td[data-title='PORT']")
            degree = soup.select("td[data-title='匿名度']")
            proxy_type = soup.select("td[data-title='类型']")
            position = soup.select("td[data-title='位置']")
            speed = soup.select("td[data-title='响应速度']")
            last_time = soup.select("td[data-title='最后验证时间']")

            # 循环验证是否有效
            for i, p, dg, pt, ps, sp, lt in zip(ip, port, degree, proxy_type, position, speed, last_time):
                ip_port = str(i.get_text()) + ':' + str(p.get_text())
                # 调用验证的方法
                flag = is_useful(ip_port, headers[header_i], target_url)
                if flag:
                    # 拼装字段
                    p_ip = str(i.get_text())
                    p_port = str(p.get_text())
                    p_degree = str(dg.get_text())
                    p_type = str(pt.get_text())
                    p_position = str(ps.get_text()).rsplit(' ', 1)[0]
                    p_operator = str(ps.get_text()).rsplit(' ')[-1]
                    p_speed = str(sp.get_text())
                    p_last_time = str(lt.get_text())

                    proxy_list.append(p_ip)
            print('End：第 %d 页结束！==========================' % (num + 1))

    except Exception as e:
        print('程序 get_proxy 发生错误，Error：', e)

    #finally:
        # 调用保存的方法
        #write_proxy(proxy_list)

    return proxy_list


def is_useful(ip_port, headers, target_url):
    """
    判断ip是否可用
    :param ip_port: ip+端口号
    :param headers: 随机请求头
    :param target_url: 爬虫的目标地址，作为验证代理池ip的有效性
    :return: bool
    """
    url = target_url    # 验证ip对目标地址的有效性
    proxy_ip = 'http://' + ip_port
    proxies = {'http': proxy_ip}
    flag = True
    try:
        requests.get(url=url, headers=headers, proxies=proxies, timeout=2)
        print("【可用】：" + ip_port)
    except Exception as e:
        print('程序 is_useful 发生错误，Error：', e)
        flag = False
    return flag




def PV(code):
    s = requests.Session()
    s.headers = firefoxHead
    count = 0

    pages = 5   # 定义爬取页数
    ua_num = 3  # 定义需生成user-agent个数
    target_url = 'https://www.baidu.com'    # 爬虫的目标地址，作为验证代理池ip的有效性
    proxy_list = get_proxy(pages, ua_num, target_url)
    #print(proxy_list)


    while True:
        count += 1
        print("正在进行第{}次访问\t".format(count), end="\t")
        #IPs = parseIPList()
        # print(random.choice(IPs))

        # IPs = ["36.248.129.106","36.248.132.123"]
        newip = random.choice(proxy_list)
        print('ip地址是{}'.format(newip))
        s.proxies = {"http: {}:9999".format(newip)}
        s.get(host)
        # r = s.get(url.format(random.choice(codes)))
        code_now=codes[random.randint(0, len(codes)-1)]
        r = s.get(url.format(code_now))
        print(code_now)
        en = html.etree.HTML(r.text)  # 将网页源代码解析成xpath对象
        result = en.xpath('//*[@id="articleContentId"]/text()')
        print(result)
        Views = en.xpath('//*[@id="mainBox"]/main/div[1]/div/div/div[2]/div[1]/div/span[2]/text()')
        print('访问量是{}'.format(Views))
        time_sleep=random.randint(8,16)
        print('下一个访问预计{}秒后'.format(time_sleep),"\r\n")
        time.sleep(time_sleep)


def main():
    PV(codes[0])
    # parseIPList()

if __name__ == "__main__":
    main()
