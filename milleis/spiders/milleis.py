import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from milleis.items import Article


class MilleisSpider(scrapy.Spider):
    name = 'milleis'
    allowed_domains = ['milleis.fr']
    start_urls = ['https://www.milleis.fr/actualites?page=1']

    def parse(self, response):
        links = response.xpath('//div[@class="carousel-white"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@aria-label="Next"]/@href').get()
        titles = response.xpath('//h3').get()
        if titles:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = "".join(response.xpath('//h1/text()').getall())
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="col-lg-8"]//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="col-lg-8"]/*[not(self::h1)]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
