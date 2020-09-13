# 虾米音乐爬虫

## 实现
### 获取歌曲id
- 访问 url 
    - 以爬取摇滚曲风的歌曲为例, 对应**曲风url**为https://www.xiami.com/genre/gid/3.
    - 曲风主页只显示前5首歌, 需要点击全部进入**全部曲风url**https://www.xiami.com/list?scene=genre&type=song&query={%22genreType%22:1,%22genreId%22:%223%22} 
    - 全部页面只展示前30首歌, 需要点击第x页进入**全部曲风分页url**https://www.xiami.com/list?page=2&query=%7B%22genreType%22%3A1%2C%22genreId%22%3A%223%22%7D&scene=genre&type=song
- 通过 url 获取 html
    - 直接用 requests.get 会失败, 需要等待页面的 javascript 加载
    - 用 selenium WebDriverWait 等待加载完毕
    - 直接获取全部曲风分页url很快会被封禁
    - 先访问曲风url, 再用selenium模拟点击进入全部曲风分页url
- 通过 html 获取 songid
    - html 中的歌曲信息格式 ``` <a href="/song/fO7s7a822">无地自容</a>```
    - 通过正则表达式解析 ``` '<a href="/song/([^"]+?)">'```

### 下载歌曲id对应的mp3音乐
- 歌曲id fO7s7a822
- 歌曲url https://www.xiami.com/song/fO7s7a822
- 直接用 youtube-dl 可以下载歌曲, ```youtube-dl --quiet --extract-audio 'https://www.xiami.com/song/fO7s7a822' -o 'fO7s7a822.%(ext)s'``` 下载到 ```f07s7a822.mp3```
- 通过 parallel 可以实现并行下载

## 环境
- centos
- python3
- 配置
    sh env.sh


## 运行
```bash
# 歌曲id写入txts
python3 xiami.py
# 根据txts下载音乐到mp3s
sh get_mp3.sh
```
