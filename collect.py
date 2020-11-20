# -*- coding: utf-8 -*-
""" 爬取指定标签(如流行)的热门播放列表, 将列表中的歌曲id写入txt文件. """

import os
import re
import time

import tqdm
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC


class XiamiCrawler:
    def __init__(self, firefox_path=None, gecko_path=None):
        binary = FirefoxBinary(firefox_path)
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        self.driver = webdriver.Firefox(
            firefox_options=opts, firefox_binary=binary, executable_path=gecko_path
        )
        self.url = "https://www.xiami.com/"
        self.collect_url = "https://www.xiami.com/collect/"
        self.collect_pattern = re.compile('<a href="/collect/([^"]+?)">')
        self.song_pattern = re.compile('<a href="/song/([^"]+?)">')

    def get_songids(
        self,
        language=None,
        max_page=5,
        page_count=30,
        dura=1,
        wait_dura=10,
    ):
        """获取指定语种(language)指定页面的所有歌单id(collect_id).

        先请求 https://www.xiami.com/, 点歌单进入歌单页面;
        歌单页面点全部标签, 选语种, 指定语种(language);
        该页面展示前30个歌单, 解析html获得collect_id;
        再点击第2页链接, 该页面展示之后30个歌单, 解析html获得collect_id;
        ...
        """
        
        # 虾米主页
        url = self.url
        self.driver.get(url)
        time.sleep(dura)
        # 点歌单
        xpath = '//*[@id="app"]/div/div[2]/div[1]/div[1]/div/div/div[1]/a[3]'
        button = self.driver.find_elements_by_xpath(xpath)[0]
        button.click()
        time.sleep(dura)
        WebDriverWait(self.driver, wait_dura).until(
            EC.presence_of_element_located((By.ID, "app"))
        )
        # 点击 全部标签, fn + f8 可以锁定javscript, 方便确定元素的xpath
        xpath = '//*[@id="app"]/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/div'
        button = self.driver.find_elements_by_xpath(xpath)[0]
        button.click()
        time.sleep(dura)
        WebDriverWait(self.driver, wait_dura).until(
            EC.presence_of_element_located((By.ID, "app"))
        )
        # 语种 上悬停鼠标
        xpath = '/html/body/nav[3]/nav[2]'
        element = self.driver.find_elements_by_xpath(xpath)[0]
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()
        time.sleep(dura)
        # 点击 华语
        if language == '华语':
            xpath = '/html/body/nav[3]/nav[2]/nav/div[1]'
        elif language == '粤语':
            xpath = '/html/body/nav[3]/nav[2]/nav/div[2]'
        elif language == '韩语':
            xpath = '/html/body/nav[3]/nav[2]/nav/div[3]'
        elif language == '欧美':
            xpath = '/html/body/nav[3]/nav[2]/nav/div[4]'
        elif language == '日语':
            xpath = '/html/body/nav[3]/nav[2]/nav/div[5]'
        else:
            raise NotImplementedError(language)
        button = self.driver.find_elements_by_xpath(xpath)[0]
        button.click()
        time.sleep(dura)
        WebDriverWait(self.driver, wait_dura).until(
            EC.presence_of_element_located((By.ID, "app"))
        )
        res = set()
        for page in range(1, max_page + 1):
            if page == 1:
                pass
            else:
                # 第page页链接
                xpath = f'//*[@id="app"]/div/div[2]/div[1]/ul/li[{min(page+1, 7)}]/a'
                button = self.driver.find_elements_by_xpath(xpath)[0]
                button.click()
                time.sleep(dura)
                WebDriverWait(self.driver, wait_dura).until(
                    EC.presence_of_element_located((By.ID, "app"))
                )
            # 点击 歌单
            desc = f'{language} {page}/{max_page}'
            for collect_ind in tqdm.tqdm(range(1, page_count + 1), desc=desc):
                # 点击第 collect_ind 个歌单
                xpath = f'//*[@id="app"]/div/div[2]/div[1]/div[2]/div[{collect_ind}]'
                button = self.driver.find_elements_by_xpath(xpath)[0]
                button.click()
                time.sleep(dura)
                WebDriverWait(self.driver, wait_dura).until(
                    EC.presence_of_element_located((By.ID, "app"))
                )
                html_str = self.driver.page_source
                songids = set(self.song_pattern.findall(html_str))
                res.update(songids)
                # 返回总歌单页面
                self.driver.execute_script("window.history.go(-1)")
                time.sleep(dura)
                WebDriverWait(self.driver, wait_dura).until(
                    EC.presence_of_element_located((By.ID, "app"))
                )
        print(language, max_page, len(res))
        return res


if __name__ == "__main__":
    """ 获取每种标签的前10个播放列表, 并将播放列表中的歌曲id写入txt. """

    XC = XiamiCrawler(
        firefox_path="driver/firefox/firefox",
        # firefox_path='/data/home/boarpeng/tor-browser_en-US/Browser/firefox',
        gecko_path="driver/geckodriver",
    )
    max_page = 5
    page_count = 30
    tag_type = 'YZ语种'
    languages = ('华语', '粤语', '日语', '韩语', '欧美')
    for language in languages:
        folder = f"txts/{tag_type}"
        if not os.path.exists(folder):
            os.mkdir(folder)
        txt_path = f"{folder}/{language}.txt"
        with open(txt_path, 'r') as fin:
            lines = fin.readlines()
        if len(lines) >= 1000:
            continue
        songids = XC.get_songids(language=language, 
                                 max_page=max_page, 
                                 page_count=page_count,
                                 dura=3)
        lines = [f"{language} {x}" for x in songids]
        with open(txt_path, "w") as fout:
            fout.write("\n".join(lines))
