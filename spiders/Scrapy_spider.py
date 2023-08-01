import scrapy
import json
import time
import re

class MySpider(scrapy.Spider):
    name = 'spider_name'
    results = []

    def parse(self, response):
        number_of_pages = self.number_page(response)
        # Парсим ссылки на товары
        for link in response.css('div.ui-card__preview.ui-card__row.ui-card__row_size_default a::attr(href)'):
            yield response.follow(link, callback=self.parse_items)

        for i in range(1, number_of_pages):
            base_url = response.url.split('?')[0]
            next_page = f'{base_url}?start={12 * i}'
            yield response.follow(next_page, callback=self.parse)

        self.make_json(response.url)

    def number_page(self, response):
        # Получаем количество страниц в категории
        pagination_list = response.css('ul.ui-pagination__list')
        pagination_items = pagination_list.css('li')
        if len(pagination_items) >= 2:
            page_element = pagination_items[-2]
            last_page_element = page_element.css('a::text').get()
            last_page_element = int(last_page_element)
            return last_page_element

    def parse_items(self, response):
        match = re.search(r"_(\d+)$", response.url)
        product_number = match.group(1) if match else None

        # Парсим  данные товара
        response_tags = response.css('div.goods-tags.goods-details-page__tags.text.text_size_small span::text').extract()
        tags = [tag.strip() for tag in response_tags]
        original_price_str = response.css('div.goods-offer-panel__price span::text').get()

        if original_price_str is not None:
            original_price = re.findall(r'\d+\.\d+|\d+', original_price_str)
            original = float(original_price[0])
            current = original
            result_sale = ((original - current) / original) * 100

            sale_tag = f"Скидка {result_sale}%"
            availability = True
        else:
            original = 0.
            sale_tag = ""
            current = original
            availability = False

        section_list = response.css('ul.ui-breadcrumbs__list li.ui-breadcrumbs__item ::text').extract()
        clean_section_list = list(filter(lambda x: x.strip(), section_list))

        result = {
            "timestamp": int(time.time()),
            'name': response.css('h1.text.text_size_display-1.text_weight_bold span::text').get(),
            "RPC": product_number,
            "url": response.url,
            "title": response.css('h1.text.text_size_display-1.text_weight_bold span::text').get(),
            "marketing_tags": tags,
            "section": clean_section_list,
            "price_data": {
                "current": current,
                "original": original,
                "sale_tag": sale_tag
            },
            "stock": {
                "in_stock": availability,
                "count": 0
            },
            "assets": {
                "main_image": f"https://apteka-ot-sklada.ru/{response.css('div.goods-gallery__active-picture-area.goods-gallery__active-picture-area_gallery_trigger img::attr(src)').get()}",
            },
            "metadata": {
                "__description": response.css('div.custom-html.content-text p').get(),
            },
            "variants": 1,
        }
        self.results.append(result)

    def make_json(self, url):
        with open(f'output_result.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)



