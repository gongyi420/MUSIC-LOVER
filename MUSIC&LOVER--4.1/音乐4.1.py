import time
import random
import requests
import json
import prettytable
from prettytable import PLAIN_COLUMNS
import pprint
from tqdm import tqdm
import os
import re
from colorama import Fore, init, Style
init()
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
notice = '请大家支持正版音乐，本产品仅适用于学习交流， 严禁商用，如希望添加其他功能，请联系作者QQ：1289354417（作者：李功易）'
print(Fore.CYAN + notice)

print(Fore.RESET + "--------------MUSIC LOVER目录-----------------")
print("1、音乐名称搜索下载       2、歌手音乐批量下载 ")
print("3、网易云音乐单曲下载     4、网易云榜单批量下载")
print("---------------------------------------------")
user = input("请输入功能的索引:")


#  酷我音乐歌曲下载及搜索功能制作
def kuwo_data():
    search = input('请输入需要搜索的歌曲:')
    kuwo_url = f"https://kuwo.cn/api/www/search/searchMusicBykeyWord?key={search}&pn=1&rn=30&httpsStatus=1&reqId=a1063621-a30b-11ed-9f29-3bb2bd0fadcc"
    #  制作展示信息的表格
    table = prettytable.PrettyTable()
    table.field_names = ['序号', '歌曲', '歌手']
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
            table.add_row([num, name, singer])
            table.align = 'l'
            table.right_padding_width = 7

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
        # print(kuwo_music_download_url)
        kuwo_music_download = requests.get(kuwo_music_download_url, stream=True)
        kuwo_download_content_size = int(kuwo_music_download.headers['Content-Length']) / 1024  # 获取大小--->实现进度条功能
        with open(f'{download_name}.mp3', mode='wb') as f:
            # f.write(kuwo_music_download.content)
            for kuwo_data in tqdm(iterable=kuwo_music_download.iter_content(1024),  # 分段请求--->实现进度条功能
                                  total=kuwo_download_content_size,
                                  unit='k',  # 单位设置
                                  ncols=100,  # 长度设置
                                  desc=f'{download_name}'):
                f.write(kuwo_data)
            print(Fore.GREEN + f'--{download_name}--下载完成^_^')
    except:
        print(Fore.YELLOW + '服务器忙碌中，正在尝试其他方法进行歌曲检索' + '')
        kuwo_user_chooseid = input("请输入歌曲的id(歌曲id查看方法详见github上README文档):")
        kuwo_user_downloadname = input("请输入歌曲名称")
        kuwo_download_url = f"http://www.kuwo.cn/api/v1/www/music/playUrl?mid={kuwo_user_chooseid}&type=mp3&httpsStatus=1&reqId=00a692f1-1adb-11ed-83a9-e917414cf877"
        kuwo_download_resp = requests.get(url=kuwo_download_url, headers=kuwo_headers)

        kuwo_download_json = kuwo_download_resp.json()
        kuwo_music_download_url = kuwo_download_json['data']['url']
        # print(kuwo_music_download_url)
        kuwo_music_download = requests.get(kuwo_music_download_url, stream=True)
        kuwo_download_content_size = int(kuwo_music_download.headers['Content-Length']) / 1024  # 获取大小--->实现进度条功能
        with open(f'{kuwo_user_downloadname}.mp3', mode='wb') as f:
            # f.write(kuwo_music_download.content)
            for kuwo_data in tqdm(iterable=kuwo_music_download.iter_content(1024),  # 分段请求--->实现进度条功能
                                  total=kuwo_download_content_size,
                                  unit='k',  # 单位设置
                                  ncols=100,  # 长度设置
                                  desc=f'{kuwo_user_downloadname}'):
                f.write(kuwo_data)
            print(Fore.GREEN + f'--{kuwo_user_downloadname}--下载完成^_^')


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
            # print(f'{music_name}----------下载完成')
            time.sleep(random.randint(0, 1))

        print(Fore.GREEN + f"{singer}专辑音乐前{pages}页全部下载完成")


def music163_download():
    music163_user = input('请输入需要下载的歌曲链接:')
    music163_name = input('请输入歌曲名称:')
    music163_id = re.findall(r'\d+', music163_user)[1]
    print(f"歌曲id:{music163_id}")
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69',
        'cookie': 'ntes_nnid=12dd9027ec4a4ff630183944202b690a,1657856871847; NMTID=00OC6KXsPguQPjxek0Pn_KEeUAzOpIAAAGCfCK8uA; WEVNSM=1.0.0; WNMCID=ptvbsq.1661608626841.01.0; WM_TID=ierGlLZTeBdEQVRFARPFDKeqkyuB3Ama; __snaker__id=CeQB3pEOogudHnEZ; _9755xjdesxxd_=32; YD00000558929251%3AWM_NI=WlaGyyjhBlGFWpRJ9lwI6ZyPyCqmyMJi8DKrZjiVvu6fxnyecJWi28QQLS%2FznECqoyeSAknwRswWUwA2ZdSbiQZg8HiBi5jK9r8JDEwEdS%2B4no9j3hYsaul0I%2BIVdG1dYzY%3D; YD00000558929251%3AWM_NIKE=9ca17ae2e6ffcda170e2e6ee9bc57ba191ffa7e15fa2ef8bb6c55a829f8f82d54db19589d1c93c9087a88cb62af0fea7c3b92a95b4afa8fc73aab88e8dc64e95b09eabbc68b597fabbfc5cbb9dbf8efc478ab7f8a5ca7a9ab6a7b7f57ff6bab88ffc6fa196998ab134938f84b4ae72ae9b8d92ee73a78d8f8ced7d92adb9b8d87d83ee9685d26aab8f9688bb44ab9ea7d6e941fbaef8abc74fb59bacb4aa40aeb1f78bb2649badaf96ef3c8bf587b7e74df3bc979bdc37e2a3; YD00000558929251%3AWM_TID=bkkyZvU0ARlFVARARALRGtPShZ0LYgg7; gdxidpyhxdE=CcylxGK8mLsXRmznHGdsVN6rRamj5yNRk5%2FL9ik2g9CsmjfOz%5Crq8j7bn2qICQuTIiudi3L6pz%2BHjdywx06sy%5ClHUvC%5CVBcS%5C3E%5CykW7Jo92o0Toc%2BDkjZ9kbMHQXu9fA%5CtEO51jd3BjvGK9oRSI8%5CtQz8pk9tdEzJvRgcbLQVwqTkb%2F%3A1664730895816; vinfo_n_f_l_n3=1516aa89ecee8a87.1.0.1673952472114.0.1673952530183; JSESSIONID-WYYY=n1ef%5CFOkvhlNFvKJ0aDM5%2F%2F%2B%2BHMO3WKDkq%2BGpqKd4sPNHYRitgtwhQtKDTCiXN%5C%2F17K2GHS7GOCwAOWuHY2%2FFfItfB%2FHr%2BiICD2TBVkfnrMXhb0Ui5iz7Kyekd6esR9DoVbbeaAhrp98pX%5CPj4cUmH6sBjy3lYXrwv7FdnA5tWesvbD4%3A1678603105014; _iuqxldmzr_=33; WM_NI=HoJj5do01k5NGJLoGWW4RPkdGy6fvSiccBQ81DVBVlbmuuWnDLLYtUd35ouyRCxblltBcZA41RzDu5YVyfJHXIGI3mcQsTxMeuB9EsuB23AssDimExvI7c8B9EkMpGvqTFc%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eed3ae4fb7eea1abd63e92e78ba3c14a828b9eacc45c908600ace84094b99cd9f12af0fea7c3b92a8cb1868bb870adf0ff8cb84685968490c65d95ec9eb1ea7085a7fa87f559abbdada3d434f39c9aa3d568a2b3bb96d666889484baf75fa8edfb90f873929db883ef68b89eadbbc440f38eb6a5f83f9b8ab787c9449c9789aab267a18fbdb5fb47a7ab8edac879b79efed4c479b19ca78ec874b697f984bb4afb9ba5aef34db6af9ca7e237e2a3'

    }
    music163_download_url = f'https://music.163.com/song/media/outer/url?id={music163_id}.mp3'
    music163_download_resp = requests.get(url=music163_download_url, headers=headers)
    music163_content_size = int(music163_download_resp.headers['Content-Length']) / 1024  # 获取大小--->实现进度条功能
    with open(f'{music163_name}.mp3', mode='wb') as f:
        # f.write(kuwo_music_download.content)
        for music163_download in tqdm(iterable=music163_download_resp.iter_content(1024),  # 分段请求--->实现进度条功能
                                      total=music163_content_size,
                                      unit='k',  # 单位设置
                                      ncols=100,  # 长度设置
                                      desc=f'{music163_name}'):
            f.write(music163_download)
        print(Fore.GREEN + f'--{music163_name}--下载完成^_^')


def music_163_batchsize():
    print(Fore.MAGENTA + '小tips:输入网址时请去掉“#/”,否则可能导致网址解析失败导致无法下载')
    user_list_url = input(Fore.RESET + "请输入需要下载的歌单网址:")

    user_file = input('请输入榜单名称:')
    os.makedirs(user_file, exist_ok=True)
    headers = {

        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'sec-fetch-dest': 'iframe',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'referer': 'https://music.163.com/',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': '_ga=GA1.2.1412864897.1553836840; _iuqxldmzr_=32; _ntes_nnid=b757609ed6b0fea92825e343fb9dfd21,1568216071410; _ntes_nuid=b757609ed6b0fea92825e343fb9dfd21; WM_TID=Pg3EkygrDw1EBAVUVRIttkwA^%^2Bn1s1Vww; P_INFO=183605463^@qq.com^|1581593068^|0^|nmtp^|00^&99^|null^&null^&null^#not_found^&null^#10^#0^|^&0^|^|183605463^@qq.com; mail_psc_fingerprint=d87488b559a786de4942ad31e080b75f; __root_domain_v=.163.com; _qddaz=QD.n0p8sb.xdhbv8.k75rl6g4; __oc_uuid=2f4eb790-6da9-11ea-9922-b14d70d91022; hb_MA-BFF5-63705950A31C_source=blog.csdn.net; UM_distinctid=171142b7a6d3ba-0fbb0bf9a78375-4313f6a-144000-171142b7a6e30b; vinfo_n_f_l_n3=6d6e1214849bb357.1.0.1585181322988.0.1585181330388; JSESSIONID-WYYY=jJutWzFVWmDWzmt2vzgf6t5RgAaMOhSIKddpHG9mTIhK8fWqZndgocpo87cjYkMxKIlF^%^2BPjV^%^2F2NPykYHKUnMHkHRuErCNerHW6DtnD8HB09idBvHCJznNJRniCQ9XEl^%^2F7^%^2Bovbwgy7ihPO3oJIhM8s861d^%^2FNvyRTMDjVtCy^%^5CasJPKrAty^%^3A1585279750488; WM_NI=SnWfgd^%^2F5h0XFsqXxWEMl0vNVE8ZjZCzrxK^%^2F9A85boR^%^2BpV^%^2BA9J27jZCEbCqViaXw6If1Ecm7okWiL^%^2BKU2G8frpRB^%^2BRRDpz8RNJnagZdXn6KNVBHwK2tnvUL^%^2BxWQ^%^2BhGf2aeWE^%^3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee84b64f86878d87f04fe9bc8fa3c84f878f9eafb65ab59498cccf48f7929fb5e72af0fea7c3b92a91b29987e670edeba8d1db4eb1af9899d64f8fb40097cd5e87e8968bd949baaeb8acae3383e8fb83ee5ae9b09accc4338aeef98bd94987be8d92d563a388b9d7cc6ef39bad8eb665a989a7adaa4197ee89d9e57ab48e8eccd15a88b0b6d9d1468ab2af88d9709cb2faaccd5e8298b9acb180aeaa9badaa74958fe589c66ef2bfabb8c837e2a3; playerid=67583529',
    }

    resp = requests.get(url=user_list_url, headers=headers)
    a = 0
    html_data = resp.text
    info_list = re.findall('<li><a href="/song\?id=(.*?)">(.*?)</a></li>', html_data)

    for info in info_list:
        a = a + 1
        new = "http://music.163.com/song/media/outer/url?id="
        music_url = new + str(info[0])
        music_name = info[1]
        music_name = re.sub('[\\\/:?"<>|]', '', music_name)
        # 访问播放链接
        music = requests.get(music_url).content
        # f = open("网易云飙升榜", music_name + ".mp3")
        with open(f"{user_file}//" + music_name + ".mp3", mode="wb") as f:
            f.write(music)
            print(str(a) + music_name + "-----下载完成")
            time.sleep(2)
    print(Fore.GREEN + f"{user_file}全部下载完成")


if __name__ == '__main__':
    while True:
        if user == '1':
            kuwo_data()
        if user == '2':
            music_batchsize()
        if user == '3':
            music163_download()
        if user == '4':
            music_163_batchsize()
        if user == 'o':
            break

