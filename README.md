
## 功能

程序尝试通过爬取行业专业类网站的文章，提取文章的标题、文本内容、发布时间、阅读人数等信息并保存到数据库中，在需要的时候从中查询，以提高信息内容的质量。

除此之外，可以对文章的内容进行分析，获取更多信息。

## 程序说明

基于python3+scrapy实现，依赖安装包存在于install_requirements文件中

支持定时执行爬虫任务:

    Linux下执行 sh install_linux.sh
    Windows下执行 install_windows.bat

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


