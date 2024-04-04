from app.leroymerlin_parser.parser import Parser
from app.model.models import Products, Product


parser = Parser()
arr = []
for i in range(1, 2):
    try:
        prods = parser.get_product_cards_from_page(i, "sad")
        for prod in prods:
            data = parser.get_product_information(prod.url, prod.vendor_code)
            arr.append(Product(
                url = data[0],
                vendor_code = data[1],
                name = data[2],
                price = data[3],
                rating = data[4],
                description = data[5],
                сharacteristics = data[6],
                photos = data[7],
                category = "sad"
                )
            )
    except Exception as e:
        print(e)

with open("sad.json", "w", encoding="utf-8") as file:
    file.write(Products(products=arr).model_dump_json())