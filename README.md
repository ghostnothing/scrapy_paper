## 功能说明

程序尝试通过爬取行业专业类网站的文章，提取文章的标题、文本内容、发布时间、阅读人数等信息并保存到数据库中，在需要的时候从中查询，以提高信息内容的质量。

除此之外，可以对文章的内容进行分析，获取更多信息。

## 软件实现

程序由python3编写，使用了开源scrapy爬虫框架，文章摘要数据存储至mysql数据库中。

## 安装说明

第一步，首先安装python3和mysql，参考官方文档

[install python3](https://www.python.org/downloads/)

[install mysql](https://www.mysql.com/downloads/)

第二步，安装python包

    pip install scrapy
    pip install numpy
    pip install sqlalchemy
    pip install ConfigParser
    pip install mysql-python
    pip install bs4

最后，如果是windows环境，需要额外安装：

[download pywin32-221.win-amd64-py3.x.exe](https://sourceforge.net/projects/pywin32/files/pywin32/Build%20221/)

## 添加定时执行爬虫任务

Linux下执行

    sh install_linux.sh

Windows下双击执行

    install_windows.bat

添加后，每间隔60分钟爬虫将会被运行。

## 网站

网站类别 |网站名称 | 支持状态
---|---|---
网络安全 | [freebuf](http://www.freebuf.com) | 支持
网络安全 | [安全客](http://bobao.360.cn/) | 支持
网络安全 | [安全牛](http://www.aqniu.com) | 支持
网络安全 | [E安全](https://www.easyaq.com/) | 支持
网络安全 | [mottoin](http://www.mottoin.com/) | 支持
网络安全 | [安全圈](https://www.sec-un.org/) | 支持
网络安全 | [安全脉搏](https://www.secpulse.com/) | 支持
网络安全 | [seebug](https://paper.seebug.org/) | 支持
网络安全 | [嘶吼](http://www.4hou.com) | 支持
网络安全 | [sec-wiki](https://www.sec-wiki.com) | 不支持
机器学习 | [我爱机器学习](http://www.52ml.net/) | 不支持


