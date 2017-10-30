from scrapy_paper.base_spider import *
HOME_PAGE = "http://www.baidu.com"


class ClassifyTitle(BaseSpider, scrapy.Spider):

    name = 'baidu_spider'

    def __init__(self, *args, **kwargs):
        super(ClassifyTitle, self).__init__(*args, **kwargs)
        if not hasattr(self, "wds"):
            self.wds = list()
        else:
            self.wds = json.loads(self.wds)
        if not hasattr(self, "max_page"):
            self.max_page = 10
        else:
            self.max_page = int(self.max_page)

    def start_requests(self):
        urls = list()
        for wd in self.wds:
            urls.append("http://www.baidu.com/s?wd={}".format(wd))
        for url in urls:
            yield scrapy.http.Request(url=url, callback=self.parse)

    def parse(self, response):
        pattern = re.compile(r'\w*"title":"(.+?)","url":"(.+?)"')
        body = response.body.decode("utf-8")
        papers = re.findall(pattern, body)
        for paper_title, paper_url in papers:
            if paper_url and paper_url.startswith("http"):
                meta_tmp = response.meta.copy()
                meta_tmp["item"] = {PAPER_TITLE: paper_title, PAPER_URL: paper_url, PAPER_SPIDER: self.name}
                yield scrapy.http.Request(url=paper_url, callback=self.parse_paper, meta=meta_tmp)

        self.page += 1
        if self.page < self.max_page:
            next_page = "{}&pn={}".format(response.url, (self.page-1)*10)
            log.debug("next_page: {}".format(next_page))
            yield scrapy.http.Request(next_page, callback=self.parse)
