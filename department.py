import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import json
from tqdm import tqdm


def askUrl(url):
    header = {
        "User-Agent": r""  ## 填写自己浏览器的请求头信息
    
    }
    req = requests.get(url=url, headers=header)
    return req
	
def get_data(bs, hos_id): # return dept datalist ,hos part of data
    if bs.title.text=='提示页':
        return -1,' ',' '
    
    # hos_id, hos_phone, hos_characterDesc, hos_address, hos_location, hos_introTrim
    hos_data = []   
    
    # dept_name:[dept_id, hos_id, dept_name, dept_belong, dept_iich_rank, dept_fdch_rank,dept_hdfurl]
    data = {}   
    
    # dept_id, dept_name, dept_belong,dept_hdfurl
    for big_dept in bs.find_all('div','item-wrap'):
        dept_belong = ''

        try:
            dept_belong = big_dept.h3.text
        except Exception as e:
            print(e)

        for small_dept in big_dept.find_all('a','faculty-item'):
            dept_id = ''
            dept_name = ''
            dept_hdfurl = ''

            try:
                t = small_dept.find_all('div','name-txt')
                if len(t)>0:
                    dept_name = t[0].text
            except Exception  as e:
                print(e)

            try:
                t = small_dept.attrs['href']
                if len(t)>0:
                    dept_hdfurl = t
                    dept_id = find_dept_id.findall(dept_hdfurl)[0]
            except Exception as e :
                print(e)
            data[dept_name] = [dept_id, hos_id, dept_name, dept_belong, -1, -1,dept_hdfurl]

    # dept_iich_rank, dept_fdch_rank
    script_data=''
    try:
        script_data = json.loads(find_script_data.findall(bs.find_all('script')[3].text)[0])
    except Exception as e:
        print(e)

    try:
        for index,rank_name in enumerate(['internetFacultyRank','fudanFacultyRank']) :
            if rank_name in script_data['keshiList']['rankList'].keys():
                for j in script_data['keshiList']['rankList'][rank_name]:
                    if j['facultyName'] in data.keys():
                        data[j['facultyName']][4+index] = j['rank']
    except Exception as e:
        print(script_data)
        print(e)
    
    hos_phone=''
    hos_characterDesc=''
    hos_address=''
    hos_location=''
    hos_introTrim=''



    try:
        hos_related_data = script_data['keshiList']['hosHeadInfo']
        hos_phone = hos_related_data['phone']
        hos_characterDesc = hos_related_data['characterDesc']
        hos_address = hos_related_data['address']
        hos_location = hos_related_data['location']
        hos_introTrim = hos_related_data['introTrim']
    except Exception as e:
        print(e)
    hos_data = [hos_id, hos_phone, hos_characterDesc, hos_address, hos_location, hos_introTrim]
    return 1,[data[i] for i in data.keys()], hos_data

find_dept_id = re.compile(r'keshi/(.*?)\.html')
find_script_data = re.compile(r'window.__INITIAL_STATE__=(.*);\(function')

baseurl = 'https://www.haodf.com/hospital/'
hos_ids = pd.read_csv('hospital_id.csv')
dept_df = pd.DataFrame(columns=['dept_id', 'hos_id', 'dept_name', 'dept_belong', 'dept_iich_rank', 'dept_fdch_rank','dept_hdfurl'])
hos_df = pd.DataFrame(columns=['hos_id', 'hos_phone', 'hos_characterDesc', 'hos_address', 'hos_location', 'hos_introTrim'])
for hos_id in tqdm(hos_ids['hos_id']):
    url = baseurl+str(hos_id)+'/keshi/list.html'
    req = askUrl(url)
    msg_code, dept_data, hos_data = get_data(BeautifulSoup(req.text),hos_id)
    
    if msg_code==-1:
        continue
    
    dept_df = dept_df.append(
        pd.DataFrame(
            dept_data,
            columns=['dept_id','hos_id','dept_name','dept_belong','dept_iich_rank','dept_fdch_rank','dept_hdfurl']
        )
    )
    hos_df.loc[len(hos_df)] = hos_data
    
    time.sleep(1)

ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
for index,text in enumerate(hos_df['hos_introTrim']):
    text = ILLEGAL_CHARACTERS_RE.sub(r'', text)
    hos_df['hos_introTrim'][index] = text
hos_df.to_excel('hos_data.xlsx',index=False,encoding='utf8')
dept_df.to_excel('dept_data.xlsx',index=False)