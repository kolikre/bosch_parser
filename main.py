import requests
import json
import csv

from lxml import html


def get_urls():
    ulr_list = []
    with open('list.txt') as my_file:
        for line in my_file:
            url = line.replace('\n', '')
            ulr_list.append(url)
    return ulr_list


def write_data_to_file(data):

    with open("products_info.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)


def parse_page(url: str = None):
    
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    }

    raw = []

    # Get page
    try:
        response = requests.get(url=url, headers=headers)
    except:
        print(f"Faided to get {url}")
        return
    
    tree = html.fromstring(response.text)

    try:
        is_404 = tree.xpath('//h1[@class="a-heading" and contains(text(), "Pagina niet gevonden")]')
    except:
        return None
    
    if is_404 != []:
        return None

    # Get product name
    try:
        product_name = str(tree.xpath('//h1[@class="a-heading"]/span/text()')[0])
        raw.append(product_name)
        # print(product_name)
    except:
        raw.append("")
        print(f"Product_name is not found in {url}")

    # Images
    try:
        separator = ", "
        images_arr = json.loads(str(tree.xpath('//script[@id="product-data"]/text()')[0]))['image']
        images = separator.join(images_arr).replace('1600x900', '2000x2000')
        raw.append(images)
        # print(images)
    except:
        raw.append("")
        print(f"Images not found in {url}")

    # Get SCU
    try:
        sku = str(tree.xpath('//span[@class="text crumb-text"]/text()')[0])
        raw.append(sku)
        # print(scu)
    except:
        raw.append("")
        print(f"SCU is not found in {url}")

    # Get Replacing codes
    try:
        separator = " "
        replacing_codes_arr = tree.xpath('//div[@class="m-producttitle"]/div//span/text()')
        replacing_codes = separator.join(replacing_codes_arr)
        raw.append(replacing_codes)
        # print(replacing_codes)
    except:
        raw.append("")
        print(f"Replacing_codes is not found in {url}")

    # Price
    try:
        price = str(tree.xpath('//div[@class="price"]//p/text()')[0]).replace(',', '.')
        raw.append(price)
        # print(price)
    except:
        raw.append("")
        print(f"Price is not found in {url}")

    # Pack
    try:
        pack = str(tree.xpath('//div[@class="details js-detail-wrapper"]/p[contains(text(),"Verpakkingseenheid")]/text()')[0]).replace('Verpakkingseenheid:', '')
        raw.append(pack)
        # print(pack)
    except:
        raw.append("")
        print(f"Pack is not found in {url}")

    # Stock
    try:
        stock = str(tree.xpath('//div[@class="stock-info-wrapper js-stock-info-wrapper"]//span[@class="text"]/text()')[0])
        raw.append(stock)
        # print(stock)
    except:
        raw.append("")
        print(f"Stock is not found in {url}")

    # Description
    try:
        separator = "\n"
        r = requests.get(url=f"https://www.bosch-home.nl/ajax/product/tabs/SHOP/{sku}", headers=headers)
        t = html.fromstring(r.text)
        description_arr = t.xpath('//div[@class="keybenefits-wrapper"]//li/text()')
        description = separator.join(description_arr)
        raw.append(description)
        # print(description)
    except:
        raw.append("")
        print(f"Description is not found in {url}")

    print(f"SKU = {sku}, Name = {product_name}, URL = {url}")

    return raw


def start():
    
    file_data = [
            ["Product name", "Image URLs", "SKU", "Replacing codes", "Price", "Pack", "Stock level", "Description"]
        ]

    url_list = get_urls()

    for url in url_list:
        product_data = parse_page(url)
        if product_data is None:
            continue
        file_data.append(product_data)
    
    write_data_to_file(file_data)


if __name__ == "__main__":
    start()

