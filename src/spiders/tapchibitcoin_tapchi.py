import time

import scrapy
from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy_playwright.page import PageMethod


def should_abort_request(req):
    if req.resource_type == "image":
        return True
    return False


class TapchibitcoinTapchiSpider(scrapy.Spider):
    name = "tapchibitcoin_tapchi"

    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": "100000",
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_request,
    }

    def start_requests(self):
        yield scrapy.Request(
            url="https://tapchibitcoin.io/tap-chi",
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    PageMethod("wait_for_selector", ".td_module_11"),
                ],
            },
            errback=self.close_page,
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        for i in range(2, 100):  # 2 to 5
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(2)
            await page.wait_for_selector(".td_module_11")

        s = Selector(text=await page.content())
        await page.close()
        for link in s.css(".td_module_11"):
            yield scrapy.Request(
                link.css(".td-read-more ::attr(href)").get(), callback=self.post_detail, meta={"playwright": False}
            )

    async def close_page(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    def post_detail(self, response):
        title = response.css(".entry-title ::Text").get()
        body = response.css(".td-post-content")
        yield {"title": title, "body": body.get()}
