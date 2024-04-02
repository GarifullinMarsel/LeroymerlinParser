from app.leroymerlin_parser.parser import Parser
from app.model.models import Products, Product

parser = Parser()

arr = []
for i in range(1, 2):
    prods = parser.get_product_cards_from_page(i, "instrumenty")
    for j in prods:
        try:
            product = parser.get_product_information(j.url)

            arr.append(Product(*product, category="instrumenty"))
        except Exception as e:
            print(e)

with open("instrumenty.json", "w", encoding="utf-8") as file:
    file.write(Products(products=arr).model_dump_json())