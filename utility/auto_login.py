# coding=utf-8
import requests
import logging
from selenium import webdriver
from get_seccode import get_verify_num
import json
import math
import time
import MySQLdb
import pymssql
import datetime

logger = logging.getLogger('auto_login_allroot')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setFormatter(formatter)
file_handler = logging.FileHandler("D:/log/auto_login_allroot.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console)


def get_headers(base_url):
    try:
        driver = webdriver.PhantomJS()
        driver.get(base_url)
        cookies_list = list()
        for ele in driver.get_cookies():
            coco = ele['name'] + "=" + ele['value']
            cookies_list.append(coco)
        cookies = ";".join(cookies_list)
        headers = {
            'Cookie': cookies,
            'Host': 'www.allroot.net',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Origin': 'http://www.allroot.net',
            'Referer': 'http://www.allroot.net/autologin.jsp',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)\
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        img = driver.find_element_by_id('seccodeimg')
        time.sleep(0.5)
        img_url = img.get_attribute('src')
        res = requests.get(img_url, headers=headers)
        with open('code.jpg', 'wb') as jpg:
            jpg.write(res.content)
        code = get_verify_num('code.jpg')
        uid_ele = driver.find_element_by_id('uid$text')
        pwd_ele = driver.find_element_by_id('pwd$text')
        sec_ele = driver.find_element_by_id('seccode$text')
        submit_ele = driver.find_element_by_partial_link_text('登录')
        if code:
            uid_ele.send_keys('cppssw')
            pwd_ele.send_keys('cppssw1988215')
            sec_ele.send_keys(code)
            submit_ele.click()
            try:
                driver.find_element_by_class_name('mini-messagebox-content-text')
                driver.close()
                get_headers(base_url)
                logger.debug("try again to login all root.")
            except:
                logger.info("login all root success!")
                out_cookies = []
                for ele in driver.get_cookies():
                    co = ele['name'] + "=" + ele['value']
                    out_cookies.append(co)
                driver.close()
                login_cookies = "; ".join(out_cookies)
                headers['Cookie'] = login_cookies
                headers['Referer'] = 'http://www.allroot.net/ebay_item.jsp?_t=128104&_winid=w6736',
                return headers

        else:
            driver.close()
            get_headers('base_url')
    except Exception as e:
        logger.error("%s while opening web driver" % e)


def auto_login(login_url, base_url):
    ebay_account = [
        "7_su061", 'buy_clothing', 'china_cheong',
        'chinafolkcollect88', 'degage88', 'east_culture_2008',
        'eeeshopping', 'fa.shion', 'fashionzone66',
        'girlspring88', 'happygirl366', 'happysmile336',
        'newfashion66', 'niceday666', 'showgirl668',
        'showtime688', 'shuai.hk', "sunshinegirl678",
    ]
    accounts = ','.join(ebay_account)
    cur_time = "%d" % (time.time() * 1000)
    headers = get_headers(login_url)
    data_page = {
        '_t': cur_time,
        'ebayid': accounts,
        'pageIndex': 1,
        'pageSize': 1

    }
    try:
        r = requests.post(base_url, data=data_page, headers=headers, timeout=60)
        json.loads(r.text)['total']
    except:
        if headers:
            headers['Referer'] = 'http://www.allroot.net/ebay_item.jsp'
    try:
        r = requests.post(base_url, data=data_page, headers=headers, timeout=60)
        number = json.loads(r.text)['total']
        page_num = int(math.ceil(number / 10000.0))
        logger.info('finish counting number of pages.')
        for page in range(0, page_num):
            data_page['pageIndex'] = page
            data_page['pageSize'] = 10000
            yield {"data": data_page, "headers": headers}
    except Exception as e:
        logger.error("%s while counting page num of items" % e)


def get_data():
    base_url = 'http://www.allroot.net/auto?auto=getebayitem'
    login_url = 'http://www.allroot.net/autologin.jsp'
    insert_query = "insert into allroot_auto values" \
                   " (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                   "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                   "%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    con = MySQLdb.connect(host='127.0.0.1', user='root', passwd='', db='tiny_tools')
    cur = con.cursor(MySQLdb.cursors.DictCursor)
    con.set_character_set('utf8')
    cur.execute('set names utf8;')
    cur.execute('set character set utf8')
    cur.execute('set character_set_connection=utf8;')
    cur.execute('truncate table allroot_auto')
    for req in auto_login(login_url, base_url):
        fails = 0
        while fails < 4:
            try:
                request = requests.post(base_url, data=req['data'], headers=req['headers'], timeout=60)
                res = json.loads(request.text)['data']
                for data in res:
                    cur.execute(insert_query, (
                        data['itemid'],
                        data['uid'],
                        data['vars'],
                        data['outofstockcontrol'],
                        data['qty'],
                        data['soldqty'],
                        data['isadvenddate'],
                        data['sku1'],
                        data['isrecommend'],
                        data['imgurl'],
                        data['sku'],
                        data['title'],
                        data['lastdate'],
                        data['isvar'],
                        data['stockqty'],
                        data['listingtype'],
                        data['starttime'],
                        data['isrelist'],
                        data['price'],
                        data['initqty'],
                        data['ebayid'],
                        data['endtime'],
                        data['minimumbestofferprice'],
                        data['issynqty'],
                        data['currency'],
                        data['lastsynqtydate'],
                        data['itemnote'],
                        data['listingduration'],
                        data['bestofferenabled'],
                        data['siteid'],
                        data['isadvshop'],
                        data['bestofferautoacceptprice'],
                        data['myrowid'],
                    ))
                    logger.info("puting %s" % data['myrowid'])
                con.commit()
                break
            except Exception as e:
                fails += 1
                logger.error('%s trying to get data from all root %s' % (e, fails))
    con.close()


def sync_mysql2py():
    mycon = MySQLdb.connect(host='127.0.0.1', user='root', passwd='', db='tiny_tools')
    mycur = mycon.cursor(MySQLdb.cursors.DictCursor)
    mycon.set_character_set('utf8')
    mycur.execute('set names utf8;')
    mycur.execute('set character set utf8')
    mycur.execute('set character_set_connection=utf8;')
    select_query = "select itemid,ebayid,isvar,max(sku1)as sku " \
                   "from allroot_auto GROUP BY itemid,ebayid,isvar "
    truncate_query = "truncate table z_allroot_listed"
    insert_query = "insert into z_allroot_listed values(%s,%s,%s,%s,getdate())"
    select_query_listed = "select count(1) as skucount,sku1 , now() " \
                          "from allroot_auto where listingtype!='Chinese'  " \
                          "group by sku1 having sku1!=' ' "
    truncate_query_listed = 'truncate table z_listed_sku_count'
    insert_query_listed = 'insert into z_listed_sku_count values(%s,%s,%s)'
    mycur.execute(select_query)
    mscon = pymssql.connect(server='121.196.233.153', user='sa',
                            password='allroot89739659', database='ShopElf',
                            port='12580', charset='utf8')
    mscur = mscon.cursor(as_dict=True)
    mscur.execute(truncate_query)
    listed = mycur.fetchall()
    for row in listed:
        try:
            mscur.execute(insert_query,
                          (row['itemid'], row['ebayid'],
                           row['sku'], row['isvar']
                           )
                          )
            logger.info("putting data to listed ")
        except Exception as e:
            logger.error('%s while putting data to listed' % e)
    mscon.commit()
    mscur.execute(truncate_query_listed)
    mycur.execute(select_query_listed)
    sku_count = mycur.fetchall()
    for row in sku_count:
        try:
            mscur.execute(insert_query_listed, (row['sku1'], row['skucount'], datetime.datetime.now()))
            logger.info('putting data to count')
        except Exception as e:
            logger.info('%s while puttding data to count' % e)

    mscon.commit()
    mycon.close()
    mscon.close()


def main():
    get_data()
    sync_mysql2py()

if __name__ == "__main__":
    main()

