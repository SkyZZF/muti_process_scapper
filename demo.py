import requests
from bs4 import BeautifulSoup
import time
import multiprocessing
import pymysql
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
}
res =[]
def request_douban(url):
   try:
       response = requests.get(url,headers = headers)
       if response.status_code == 200:
           return response.text
   except requests.RequestException:
       return None
def content_info(url):
    html = request_douban(url)
    soup = BeautifulSoup(html, 'lxml')
    list = soup.find(class_='grid_view').find_all('li')

    for item in list:
        item_name = item.find(class_='title').string
        item_img = item.find('a').find('img').get('src')
        item_index = item.find(class_='').string
        item_score = item.find(class_='rating_num').string
        _item = item.find('p').text
        _item = _item.split("\n")
        item_author = _item[1].strip()
        item_tag = _item[2].strip()
        item_intr = item.find(class_='inq').string if item.find(class_='inq') else "无"
        db = pymysql.connect(host='localhost', user='root', password='password', port=3306, db='douban_movie')
        cursor = db.cursor()

        #可减少插入数据出错的概率
        item_tag = db.escape_string(item_tag)
        item_author = db.escape_string(item_author)
        item_intr = db.escape_string(item_intr)

        sql = '''INSERT INTO movie (movie_index,movie_name,img,score,author,tag,introduction) VALUES({},'{}','{}','{}','{}','{}','{}') ''' .format(int(item_index),item_name,item_img,item_score,item_author,item_tag,item_intr)
        cursor.execute(sql)
        db.commit()
        db.close()

def muti_process_scapper(url_lists):

    '''

    定义多进程爬虫调用函数，使用mutiprocessing模块爬取web数据

    '''

    begin_time = time.time()

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    pool.map(content_info,url_lists)

    end_time = time.time()

    print ("%d个进程爬虫爬取所耗费时长为:%s" % (multiprocessing.cpu_count(),(end_time - begin_time)))
def scapper(url_lists):
    begin_time = time.time()
    for url in url_lists:
        content_info(url)
    end_time = time.time()
    print("单进程爬虫爬取所耗费时长为:%s" % (end_time - begin_time))
def main():
    urls = []
    for i in range(0, 10):
        url = 'https://movie.douban.com/top250?start=' + str(i * 25) + '&filter='
        urls.append(url)
    muti_process_scapper(urls)
    # scapper(urls)
if __name__ == '__main__':
    main()