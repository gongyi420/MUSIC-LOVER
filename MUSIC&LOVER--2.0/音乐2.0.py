import time
import random
import requests
import json
import prettytable
import pprint
from tqdm import tqdm
import os
kuwo_headers = {
        'Cookie': '_ga=GA1.2.1814122629.1651482273; _gid=GA1.2.205632186.1660292719; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1660292719,1660351648; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1660374742; kw_token=2CX2HIT8EYG',
        'csrf': '2CX2HIT8EYG',
        'Referer': f'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',  # 必须设置防盗链
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}

welcome = '''
                __  ___           _      __                        
               /  |/  /_  _______(_)____/ /   ____ _   _____  _____
              / /|_/ / / / / ___/ / ___/ /   / __ \ | / / _ \/ ___/
             / /  / / /_/ (__  ) / /__/ /___/ /_/ / |/ /  __/ /    
            /_/  /_/\__,_/____/_/\___/_____/\____/|___/\___/_/     
'''
print(welcome)
notice = '请大家支持正版音乐，本产品仅适用于学习交流， 严禁商用，如希望添加其他功能，请联系作者：1289354417（原作者：李功易）'
print(notice)
print("--------------MUSIC LOVER目录-----------------")
print("1、音乐名称搜索下载       2、歌手音乐批量下载 ")
print("---------------------------------------------")
user = input("请输入功能的索引:")
#  酷我音乐歌曲下载及搜索功能制作
def kuwo_data():
    search = input('请输入需要搜索的歌曲:')
    kuwo_url = f"https://kuwo.cn/api/www/search/searchMusicBykeyWord?key={search}&pn=1&rn=30&httpsStatus=1&reqId=a1063621-a30b-11ed-9f29-3bb2bd0fadcc"
    #  制作展示信息的表格
    table = prettytable.PrettyTable()
    table.field_names = ['序号', '歌曲', '歌手', '歌曲id']
    downloads_list = []  # 创建一个歌曲列表--->存放歌曲rid
    try:
        kuwo_response = requests.get(url=kuwo_url, headers=kuwo_headers)
        musics = kuwo_response.json()
        music_data = musics['data']['list']
        num = 0  # 序号
        for music in music_data:
            num = num + 1
            name = music['name']  # 歌曲名称
            singer = music['artist']  # 作者
            album = music['album']  # 专辑名称
            musicrid = music['musicrid']  # 歌曲未处理的rid
            rid = musicrid.split('_')[1]  # 处理后的歌曲rid  # split以’_‘分割后取第一个字符串
            table.add_row([num, name, singer, rid])
            table.align = 'l'
            if num > 7:  # 只保留前八条信息
                break
            downloads_list.append(rid)
            downloads_list.append(name)


        print(table)

        # 歌曲下载功能
        user_choose = input('请输入需要下载的歌曲序号:')
        choose = int(user_choose) - 1
        download_choose = downloads_list[choose]  # 在列表里提取到相应的歌曲rid
        kuwo_name = int(user_choose) * 2 - 1  # 在downloads_list列表中如果选择的序号为第一个，那么对应名字索引为1，若序号为2，对应索引为3--->找规律
        download_name = downloads_list[kuwo_name]

        kuwo_download_url = f"http://www.kuwo.cn/api/v1/www/music/playUrl?mid={download_choose}&type=mp3&httpsStatus=1&reqId=00a692f1-1adb-11ed-83a9-e917414cf877"
        kuwo_download_resp = requests.get(url=kuwo_download_url, headers=kuwo_headers)
        kuwo_download_json = kuwo_download_resp.json()
        kuwo_music_download_url = kuwo_download_json['data']['url']
        kuwo_music_download = requests.get(kuwo_music_download_url, stream=True)
        kuwo_download_content_size = int(kuwo_music_download.headers['Content-Length'])/1024  # 获取大小--->实现进度条功能
        with open(f'{download_name}.mp3', mode='wb')as f:
            #f.write(kuwo_music_download.content)
            for kuwo_data in tqdm(iterable=kuwo_music_download.iter_content(1024),  # 分段请求--->实现进度条功能
                 total=kuwo_download_content_size,
                 unit='k',  # 单位设置
                 ncols=100,  # 长度设置
                 desc=f'{download_name}'):
                f.write(kuwo_data)
            print(f'--{download_name}--下载完成^_^')
    except:
        print('服务器错误，请稍后重试')


def music_batchsize():
    singer = input('请输入需要下载的歌手姓名:')
    pages = int(input(f'请输入需要下载{singer}歌曲的页数:'))
    os.makedirs(f"{singer}音乐专辑", exist_ok=True)
    for page in range(1, pages + 1):
        batch_url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={singer}&pn={page}&rn=30&httpsStatus=1&reqId=7b7b91a0-1ad7-11ed-b9a8-198e9cc3d87a'
        batch_response = requests.get(url=batch_url, headers=kuwo_headers)
        # 解析数据 找到音乐的下载地址
        json_data = json.loads(batch_response.text)  # 解析后的数据 为字典类型
        lists = json_data['data']['list']
        # 相关准备
        rid_box = []  # 建立一个列表用来存储音乐rid
        name_box = []  # 建立一个列表用来存储音乐名称
        download_box = []  # 建立一个列表用来存放下载链接
        num = 0  # 序号

        for lis in lists:
            rid_box.append(lis['rid'])
            name_box.append(lis['name'])

        for rid in tqdm(rid_box, ncols=100, desc=f"{singer}音乐专辑下载ing"):
            music_name = name_box[num]
            num = num + 1
            music_url = f'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=mp3&httpsStatus=1&reqId=00a692f1-1adb-11ed-83a9-e917414cf877'
            music_response = requests.get(music_url)
            music_dic = json.loads(music_response.text)
            batch_download = music_dic['data']['url']

            download_box.append(batch_download)
            # 下载音乐

            f = open(f'{singer}音乐专辑/{music_name}.mp3', 'wb')
            load_music = requests.get(batch_download)
            f.write(load_music.content)  # 下载音乐
            #print(f'{music_name}----------下载完成')
            time.sleep(random.randint(0, 1))


        print(f"{singer}专辑音乐前{pages}全部下载完成")




if __name__ == '__main__':
    if user =='1':
        kuwo_data()
    if user =='2':
        music_batchsize()