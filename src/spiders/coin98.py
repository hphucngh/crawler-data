import json
import time
from ast import literal_eval

import scrapy
from scrapy.selector import Selector
from scrapy_playwright.page import PageMethod


def should_abort_request(req):
    if req.resource_type == "image":
        return True
    return False


class Coin98Spider(scrapy.Spider):
    name = "coin98"
    allowed_domains = ["coin98.net", "insights.coin98.com"]
    start_urls = ["https://coin98.net/menu/buidl"]

    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": "100000",
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_request,
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Accept": "application/json",
        "Connection": "keep-alive",
    }

    def start_requests(self):
        yield scrapy.Request(
            url="https://coin98.net/menu/buidl",
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    PageMethod("wait_for_selector", ".style_customCol__lCKbT"),
                ],
            },
            errback=self.close_page,
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        for i in range(2, 10):
            time.sleep(2)
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(2)
            await page.wait_for_selector(".style_insightsFooter__sw4x4")

        s = Selector(text=await page.content())
        await page.close()
        for link in s.css("div.style_cardInsight__F9av_"):
            # Do mỗi 1 style_no-underline__FM_LN có nhiều hơn 2 thẻ a style_no-underline__FM_LN, link bài viết và link tác giả
            for detail in link.css(".style_no-underline__FM_LN"):
                link_post = detail.css("a::attr(href)").get()
                if len(link_post) > 1:
                    print("===> ", link_post)
                    yield scrapy.Request(
                        f"https://insights.coin98.com/adapters/post/slug{link_post}",
                        callback=self.post_detail,
                        headers=self.headers,
                        meta={"playwright": False},
                    )
                break

    async def close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    def post_detail(self, response):
        yield json.loads(response.body)

        # title = response.css(".header-layout__title ::Text").get()
        # detail_body = self.parse_body(response)
        # if not title:
        #     title = response.css("h1.style_title__pYoQc ::Text").get()
        # yield {"title": title, "detail_bodys": detail_body}

    def parse_body(self, response):
        detail_body = {}
        print("111111111")
        for p in response.css("#layout-normal-minHeight"):
            print("========")
            des = ""
            det = ""
            if p.css("h2"):
                if det != p.css("h2 ::Text").get():
                    detail_body.update({"key": det, "value": des})
                    des = ""
                det = p.css("h2 ::Text").get()
            if p.css("p"):
                des += p.css("p ::Text").get()
        return detail_body
