"""
网络视频下载器
需要输入的参数:
url:        网页地址
save_path:  保存地址

注意:cookie参数需要自行设置
"""
from selenium import webdriver
import os
from bs4 import BeautifulSoup
import urllib.request
import shutil


def download(save_path, video_title, get_ts, save_temp):
    """
    这个函数会存在问题,使用了绝对路径，需要使用者再单独修改
    """
    ts_list = "concat:"
    for ts in get_ts:
        try:
            shutil.copy(f"{save_path}/downTool.exe", f"{save_path}/temp")
            os.system(f"E: && cd {save_path}/temp && downTool.exe {ts}")
            ts_list += f"{save_path}/temp/{ts.split('/')[-1].split('.')[0]}-{ts.split('/')[-1]}|"
        except:
            pass

    try:
        state = os.system(f'ffmpeg -i "{ts_list}" -c copy {save_path}/{video_title}.ts')
    except:
        state = 1
    if state == 1:
        state = os.system(f'ffmpeg -i "{ts_list}" -c copy {save_path}/output.ts')
    if not(save_temp) and state == 0:
        shutil.rmtree(f"{save_path}/temp")


def get_ts_list(save_path, url):
    options = webdriver.ChromeOptions()
    # 关闭可视化
    options.add_argument('--headless')
    prefs = {'profile.default_content_settings.popups': 0}
    options.add_experimental_option("prefs", prefs)
    wb = webdriver.Chrome(options=options)

    # 登录页面
    wb.get(url)
    wb.implicitly_wait(5)

    cookies = ""
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        wb.add_cookie(cookie)
    wb.refresh()
    wb.get(url)

    # 将页面转换为html格式
    soup = BeautifulSoup(wb.page_source, "html.parser")
    section_elements = soup.find_all("script")
    # print(section_elements)
    for section in section_elements:
        for d in section:
            if "html5player.setVideoHLS" in d:
                for line in str(d).split(';'):
                    if "html5player.setVideoTitle" in line:
                        video_title = line.strip().split("'")[1]
                        os.makedirs(f"{save_path}/temp", exist_ok=True)
                        # print(f"视频名称:{video_title}")
                    if ".m3u8" in line:
                        m3u8_url = line.strip().split("'")[1]
                        urllib.request.urlretrieve(m3u8_url, f"{save_path}/temp/temp.m3u8")

                        with open(f"{save_path}/temp/temp.m3u8") as temp_m3u8:
                            m3u8_data = temp_m3u8.readlines()

                        # 选择下载的分辨率
                        frame_ratio_list = ["1080p", "720p", "480p"]
                        for frame_ratio in frame_ratio_list:
                            for line in m3u8_data:
                                # print(frame_ratio)
                                if frame_ratio in line and "m3u8" in line:
                                    # 源头链接
                                    meta_url = m3u8_url.strip().split("hls.m3u8")[0]

                                    urllib.request.urlretrieve(meta_url + line, f"{save_path}/temp/temp.ts")
                                    with open(f"{save_path}/temp/temp.ts") as temp_ts:
                                        ts_data = temp_ts.readlines()

                                    ts_list = []
                                    for line in ts_data:
                                        if ".ts" in line:
                                            ts_list.append(meta_url + line.strip())
                                    return video_title, ts_list

    print("被限制")
    return None, None


if __name__ == "__main__":
    # 配置数据
    url = ""
    save_path = ""
    # 是否保存临时文件,默认为False
    save_temp = False

    # 获取到需要下载的ts链接列表
    video_title, get_ts = get_ts_list(save_path, url)
    # 下载ts视频流，合并视频流
    download(save_path, video_title, get_ts, save_temp)
    print(f"视频下载完成")
