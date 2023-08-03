import scrapy
from scrapy_playwright.page import PageMethod


def should_abort_request(req):
    if req.resource_type == "image":
        return True
    if req.method.lower() == "post":
        return True
    return False


class TutorialSpider(scrapy.Spider):
    name = "tutorial"
    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": "100000",
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_request,
    }

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.lazada.com.my/shop-laptops-gaming/",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", '[data-tracking="product-card"]'),
                ],
            },
        )

    def parse(self, response):
        products_selector = response.css('[data-tracking="product-card"]')

        for product in products_selector:
            link = response.urljoin(product.xpath(".//a[text()]/@href").get())
            yield scrapy.Request(link, callback=self.parse_product, meta={"playwright": False})

    def parse_product(self, response):
        yield {
            "Product": response.css(".pdp-mod-product-badge-title ::Text").get(),
            "Price": response.css(".pdp-price_color_orange ::Text").get(),
        }
