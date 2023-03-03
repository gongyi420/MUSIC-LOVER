import requests
import json
import prettytable
import pprint
from tqdm import tqdm
headers = {
        'Cookie': '_ga=GA1.2.1814122629.1651482273; _gid=GA1.2.205632186.1660292719; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1660292719,1660351648; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1660374742; kw_token=2CX2HIT8EYG',
        'csrf': '2CX2HIT8EYG',
        'Referer': f'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',  # 必须设置防盗链
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}

search = input('请输入需要搜索的歌曲:')
#  制作展示信息的表格
table = prettytable.PrettyTable()
table.field_names = ['序号', '歌曲', '歌手', '歌曲id']
#  酷我音乐歌曲下载及搜索功能制作
def kuwo_data(kuwo_url):
    try:
        downloads_list = []  # 创建一个歌曲列表--->存放歌曲rid
        kuwo_response = requests.get(url=kuwo_url, headers=headers)
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
        kuwo_download_resp = requests.get(url=kuwo_download_url, headers=headers)
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


if __name__ == '__main__':
    kuwo_url = f"https://kuwo.cn/api/www/search/searchMusicBykeyWord?key={search}&pn=1&rn=30&httpsStatus=1&reqId=a1063621-a30b-11ed-9f29-3bb2bd0fadcc"
    kuwo_data(kuwo_url)
