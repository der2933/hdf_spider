import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


def askUrl(url):
    header = {
        "User-Agent": r""  ## 填写自己浏览器的请求头信息
    }

    req = requests.get(url=url, headers=header)

    return req
	
def get_data(req):
    bs = BeautifulSoup(req.text)
    province_name = re.findall(find_province_name, bs.title.text)[0]
    city_name = []
    hospital_datalist = []  # 医院id, 医院名称, 省份, 地级市, 医院等级, 特色, 好大夫url
    data_list = []

    for cn in bs.find_all('div','m_title_green'):
        city_name.append(cn.text)

    for index,hospitals in enumerate(bs.find_all('div','m_ctt_green')):
        data = []
        for hos in hospitals.find_all('li'):
            text = ''
            hos_id = ''
            hos_name = ''
            hos_rank = ''
            hos_featu = ''
            hos_hdfurl = ''

            text = hos.prettify()
            hos_name = hos.a.text
            try:
                t = re.findall(find_hos_id, text)
                if len(t)>0:
                    hos_id = t[0]
            except Exception as e:
                print(e)

            try:
                t = re.findall(find_hos_features,text)
                if len(t)>0:
                    if len(t[0])>=3:
                        hos_rank = t[0].split(',')[0]
                        hos_featu = t[0].split(':')[-1]
                    else :
                        hos_rank = t[0]
            except Exception as e:
                print(e)

            try:
                t = re.findall(find_hos_url,text)
                if len(t)>0:
                    hos_hdfurl = t[0];
            except Exception as e:
                print(e)

            data.append([hos_id,hos_name,province_name,city_name[index],hos_rank,hos_featu,hos_hdfurl])
        data_list += data
    return pd.DataFrame(data_list,columns=['hos_id','hos_name','hos_prov','hos_city','hos_grad','hos_featu','hos_hdfurl'])
	

find_province_name = re.compile(r'(.*?)全部医院_好大夫在线')
find_hos_url = re.compile(r'<a href="(.*?)"')
find_hos_id = re.compile(r'hospital/(.*?).html')
find_hos_features = re.compile(r'\((.*?)\)')

baseurl = 'https://www.haodf.com/hospital/list-'
df = pd.DataFrame(columns=['hos_id','hos_name','hos_prov','hos_city','hos_grad','hos_featu','hos_hdfurl'])
for i in [11,12,13,14,15,21,22,23,31,32,33,34,35,36,37,41,42,43,44,45,46,50,51,52,53,54,61,62,63,64,65]:
    url = baseurl+str(i)+'.html'
    print(url)
    req = askUrl(url)
    province_df = get_data(req)
    df = df.append(province_df)
    time.sleep(5)
df.to_csv('hospital.csv',index=False,encoding='utf8')
df.to_excel('hospital.xlsx',index=False,encoding='utf8')
df['hos_id'].to_csv('hospital_id.csv',index=False)