import pymssql


def get_unlisted_products(
        begin_date,
        end_date,
        store_owner='',
        store_name='',
        goods_status='',
        saler_name1='',
        saler_name2='',
        cat_name1='',
        cat_name2='',
):

    con = pymssql.connect(
        server='121.196.233.153',
        user='sa',
        password='allroot89739659',
        database='ShopElf',
        port='12580'
    )
    cur = con.cursor(as_dict=True)

    sql = "www_checklisted_products '%s','%s','%s','%s','%s','%s','%s','%s','%s'" % (
        begin_date, end_date, store_owner, store_name, goods_status,
        saler_name1, saler_name2, cat_name1, cat_name2
    )
    try:
        cur.execute(sql)
        for row in cur.fetchall():
            yield row
    except Exception as e:
        print "%s while trying to get data from py" % e
    finally:
        con.close()

if __name__ == '__main__':
    get_unlisted_products('2015-01-01', '2017-02-02')
