# -*- coding: utf-8 -*-
""" 爬取指定标签(如流行)的热门播放列表, 将列表中的歌曲id写入txt文件. """

import os
import re
import time

import tqdm
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class XiamiCrawler:
    def __init__(self, firefox_path=None, gecko_path=None):
        binary = FirefoxBinary(firefox_path)
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        self.driver = webdriver.Firefox(
            firefox_options=opts, firefox_binary=binary, executable_path=gecko_path
        )
        self.url = "https://www.xiami.com/genre/gid/"
        self.page_url = ("https://www.xiami.com/list?page=<page>"
                         "&query=%7B%22genreType%22%3A1%2C%22genreId%22%3A%22<tagid>%22%7D"
                         "&scene=genre&type=song")
        self.song_pattern = re.compile('<a href="/song/([^"]+?)">')

    def get_html(self, url=None, page=None):
        """ 获取 url 对应的 html 文本. """

        if page == 1:
            self.driver.get(url)
            xpath = '//*[@id="app"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/a/div/div'
        else:
            # xpath = '//*[@id="app"]/div/div[2]/div[1]/ul/li[3]/a'
            xpath = f'//*[@id="app"]/div/div[2]/div[1]/ul/li[{page+1}]/a'
        python_button = self.driver.find_elements_by_xpath(xpath)[0]
        python_button.click()
        time.sleep(3)
        html_str = self.driver.page_source
        return html_str

    # def get_songids_direct(
    #     self,
    #     tag=None,
    #     tagid=None,
    #     max_page=5,
    #     page_count=30,
    #     dura=1,
    #     wait_dura=10,
    # ):
    #     """获取指定标签id(tagid)的所有歌曲id(songid).
    #
    #     直接访问指定标签id<tagid>页面<page>的url,
    #     ('https://www.xiami.com/list?page=<page>'
    #      '&query=%7B%22genreType%22%3A1%2C%22genreId%22%3A%22<tagid>%22%7D'
    #      '&scene=genre&type=song');
    #     等待 <div id="app"> 加载;
    #     解析 html 得到 songid;
    #
    #     直接访问容易被禁
    #     """
    #     songids = []
    #     for page in tqdm.tqdm(range(1, max_page + 1), desc=tag):
    #         url = self.page_url.replace("<tagid>", tagid).replace("<page>", str(page))
    #         self.driver.get(url)
    #         time.sleep(dura)
    #         WebDriverWait(self.driver, wait_dura).until(
    #               EC.presence_of_element_located((By.ID, "app"))
    #         )
    #         html_str = self.driver.page_source
    #         page_songids = self.song_pattern.findall(html_str)
    #         page_songids = [x for x in page_songids if "undefined" not in x]
    #         assert len(page_songids) == page_count
    #         songids.extend(page_songids)
    #     assert len(set(songids)) == page_count * max_page
    #     return songids

    def get_songids(
        self,
        tag=None,
        tagid=None,
        max_page=5,
        page_count=30,
        dura=1,
        wait_dura=10,
    ):
        """获取指定标签id(tagid)的所有歌曲id(songid).

        先请求 https://www.xiami.com/genre/gid/<tagid>, 该页面展示5首歌;
        再点击页面的全部按钮, 该页面展示前30首歌, 解析html获得songid;
        再点击第2页链接, 该页面展示之后30首歌, 解析html获得songid;
        ...
        """

        url = self.url + tagid
        songids = []
        for page in tqdm.tqdm(range(1, max_page + 1), desc=tag):
            if page == 1:
                self.driver.get(url)
                # 全部按钮
                xpath = (
                    '//*[@id="app"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/a/div/div'
                )
            else:
                # 第page页链接
                xpath = f'//*[@id="app"]/div/div[2]/div[1]/ul/li[{page+1}]/a'
            python_button = self.driver.find_elements_by_xpath(xpath)[0]
            python_button.click()
            time.sleep(dura)
            WebDriverWait(self.driver, wait_dura).until(
                EC.presence_of_element_located((By.ID, "app"))
            )
            html_str = self.driver.page_source
            page_songids = self.song_pattern.findall(html_str)
            page_songids = [x for x in page_songids if "undefined" not in x]
            songids.extend(page_songids)
            assert len(page_songids) == page_count
        assert len(set(songids)) == max_page * page_count
        return songids


if __name__ == "__main__":
    """ 获取每种标签的前10个播放列表, 并将播放列表中的歌曲id写入txt. """

    XC = XiamiCrawler(
        firefox_path="driver/firefox/firefox",
        # firefox_path='/data/home/boarpeng/tor-browser_en-US/Browser/firefox',
        gecko_path="driver/geckodriver",
    )
    type2tags = {
        "Genre曲风": [
            ("Pop流行", "2"),
            ("Rock摇滚", "3"),
            ("Folk民谣", "16"),
            ("Electronic电子", "9"),
            ("R&B节奏布鲁斯", "10"),
            ("Jazz爵士", "5"),
            ("EasyListening轻音乐", "12"),
            ("HipHop嘻哈(说唱)", "1"),
            ("ACG动漫", "24"),
            ("Blues布鲁斯", "4"),
            ("Metal金属", "18"),
            ("Punk朋克", "25"),
            ("NewAge新世纪", "13"),
            ("Country乡村", "20"),
            ("Reggae雷鬼", "6"),
            ("Classical古典", "21"),
            ("Latin拉丁", "8"),
            ("Children儿童", "22"),
        ],
    }
    for tag_type, tags in type2tags.items():
        for (tag, tagid) in tags:
            folder = f"txts/{tag_type}"
            if not os.path.exists(folder):
                os.mkdir(folder)
            txt_path = f"{folder}/{tag}.txt"
            # check num
            if tagid != "1":
                if os.path.exists(txt_path):
                    with open(txt_path, "r") as fin:
                        lines = fin.readlines()
                    if len(lines) >= 30 * 5:
                        print(f"{tag} done", flush=True)
                        continue
            # songids = XC.get_songids_direct(tag=tag, tagid=tagid)
            songids = XC.get_songids(tag=tag, tagid=tagid)
            lines = [f"{tag} {x}" for x in songids]
            with open(txt_path, "w") as fout:
                fout.write("\n".join(lines))
