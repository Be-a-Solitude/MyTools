import requests
import pymysql
import time
import json
import parsel

headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

def get_proxy(page):
    
    print('++++++++++++++++正在获取第{}页的代理++++++++++++++++'.format(page),'\n')
    url = 'https://www.kuaidaili.com/free/inha/{}'.format(page)
    response = requests.get(url,headers=headers)
    html_data = parsel.Selector(response.text)
    parsel_list = html_data.xpath(
        '//table[@class="table table-bordered table-striped"]/tbody/tr'
    )
    proxy_dict={}
    id = 1
    for tr in parsel_list:
        each_proxy = {}
        ip = tr.xpath("./td[1]/text()").extract_first()
        port = tr.xpath("./td[2]/text()").extract_first()
        each_proxy[ip] = port
        proxy_dict['{}'.format(id)] = each_proxy
        id = id + 1
    print(proxy_dict,'\n')
    return proxy_dict

def check_ip(proxy_dict):
    can_use = {}
    proxy_can_use = {}
    mid = 1
    for key in proxy_dict.keys():
        for proxy in proxy_dict[key].keys():
            ip = proxy
        for port in proxy_dict[key].values():
            ip_port =port
        print('+++++++++++++++++ mid: ',mid,',正在检查ip: [{}] 是否可用 +++++++++++++++++'.format(ip+':'+ip_port))
        check_proxy = {'http': ip + ':' + ip_port}
        try :
            response = requests.get('https://www.baidu.com',headers=headers,proxies=check_proxy,timeout=0.1)
            if response.status_code == 200 :
                check_proxy[ip] = port
                can_use[mid] = check_proxy 
                print("当前ip: ",check_proxy," 检测通过\n")
        except Exception as e:
            print (e,"\n")
        mid+=1
    return can_use


def conserve_in_database(DatabaseName,content):
    try:
        db = pymysql.connect(
            host = 'localhost',
            user = 'proxy', 
            password = 'rExQpekQFjks',
            database = 'proxies_pool',
            charset ='utf8'
        )
    except:
        print("Connect Error!!!!!")
    
    try:
        cur = db.cursor()
    except Exception as e:
        print(e)
    print("+ + + + + +连接成功+ + + + + +")
    sql = "SELECT * FROM proxies"
    mid = cur.execute(sql)
    for key in content.keys():
        print("+++++++++++++++++++++++++++++")
        print(content[key])
        for proxy in content[key].keys():
            ip = proxy
        for port in content[key].values():
            ip_port =port
        sql = "INSERT INTO proxies(id,ip,port) \
                VALUES('%d','%s','%s')" % \
                (mid,ip,ip_port)
        try :
            cur.execute(sql)
            db.commit()
            print("++++++++ Insert Successfully! ++++++++",'\n')
        except Exception as e:
            print(e)
            print ('插入数据失败!')
            db.rollback()
        mid+=1


def out_proxy():
    out_ip={}
    ip_sql= "SELECT * FROM proxies WHERE id >= ((SELECT MAX(id) FROM proxies)-(SELECT MIN(id) FROM proxies)) * RAND() + (SELECT MIN(id) FROM proxies) LIMIT 1"
    try:
        db = pymysql.connect(
            host = 'localhost',
            user = 'proxy', 
            password = 'rExQpekQFjks',
            database = 'proxies_pool',
            charset ='utf8'
        )
        print("++++++ 连接成功 ++++++")
        cur = db.cursor()
        try :
            cur.execute(ip_sql)
            temp = cur.fetchone()
            db.commit()
            print("++++++++ 获取数据成功! ++++++++")
            out_ip = {'http':temp[1] + ':' + temp[2]}
        except Exception as e:
            print ('获取数据失败!')
            print(e)
            db.rollback()
        
    except Exception as e:
        print("connect error")
    return out_ip

def main():
    for page in range(200,250):
        content = get_proxy(page)
        print(len(content),"\n")
        can_use =check_ip(content)
        conserve_in_database('proxies_pool',can_use)

main()
