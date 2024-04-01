import abc
import random
import requests
from bs4 import BeautifulSoup
from typing import List, Literal, Dict

from app.model.models import CardProduct, Characteristic, Product



class BaseParser(abc.ABC):
    base_url = "https://leroymerlin.ru/"
    base_api_url = "https://api.leroymerlin.ru/"
    headers = {
        'Host': 'api.leroymerlin.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': 'uid_experiment=8431b60b53e41c2a3251286913c6deb5; pageExperiments=plp_recommendations:B+srp_category_facet:B; _regionID=34; iap.uid=bed2705a46ee418687b0fe8f417ad881; ___dmpkit___=ab4ba242-8804-427c-9c45-22d77fd8a979; _bge_ci=BA1.1.6583670419.1710801713; aplaut_distinct_id=JLTCsuJ2POyw; uxs_uid=b72d7570-e578-11ee-931c-6901b5025b71; kameleoonVisitorCode=l200u3djm8kovq4o; tmr_lvid=93b9eecc834dcca30e45523ad541e3cd; tmr_lvidTS=1710801713702; _ym_uid=1710801714352854536; _ym_d=1710801714; _gpVisits={"isFirstVisitDomain":true,"idContainer":"10002546"}; cookie_accepted=true; user-geolocation=0%2C0; tmr_detect=1%7C1711999452226; GACookieStorage=undefined; X-API-Experiments-sub=B; qrator_jsid=1711997406.977.xLTkuDpUN0wDIxff-e2olov1vosa469pb0otd5ujps3panapr; _ym_isad=1; _gp10002546={"hits":8,"vc":1,"ac":1,"a6":1}; _ym_visorc=b',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'x-api-key': 'nkGKLkscp80GVAQVY8YvajPjzaFTmIS8',
        'x-request-id': '7ab6ae82049d4f980540e87971faf0cf'
    }
    

    def get_product_cards_from_page(self, 
            page: int, 
            catalog: Literal["dveri", "kraski", "instrumenty", "sad"]
        ) -> List[CardProduct]:
        response = requests.get(self.base_url + f"catalogue/{catalog}/?page={page}/", headers=self.headers)
        if response.status_code != 200:
            raise RuntimeError(f"все плохо, братик, статус: {response.status_code}")

        soup = BeautifulSoup(response.text, "lxml")
        products = []
        for i in soup.find_all("a", class_="bex6mjh_plp b1f5t594_plp p5y548z_plp pblwt5z_plp nf842wf_plp"):
            product_url = self.base_url+i.get("href")
            products.append(CardProduct(url=product_url))
        return products

    def _get_vendor_code(self, url: str) -> int:
        page = requests.get(url, headers=self.headers).text
        soup_page = BeautifulSoup(page, "lxml")
        code = soup_page.find("span", class_="t12nw7s2_pdp")
        if code is None:
            raise RuntimeError("не удается получичть артикул")
        return int(code.text[2:])

    @staticmethod
    def _get_name(raw_product_info: Dict) -> str:
        try:
            name = raw_product_info.get("content")[0].get("displayedName")
        except Exception:
            raise RuntimeError("не удалось распарсить название товара из жсон")
        return name
    
    @staticmethod
    def _get_price(raw_product_info: Dict) -> int:
        try:
            price = raw_product_info.get("content")[0].get("price").get("main_price")
        except Exception:
            raise RuntimeError("не удалось распарсить цену товара из жсон")
        return price
    
    @staticmethod
    def _get_description(raw_product_info: Dict) -> str:
        try:
            description = raw_product_info.get("content")[0].get("marketingDescription").replace("\n", "<br>").replace("**", "").replace("###", "")
        except Exception:
            raise RuntimeError("не удалось распарсить описание из жсон")
        return description  
    
    def _get_сharacteristics(self, vendor_code: int) -> List[Characteristic]:
        try:
            url = self.base_api_url + f"experience/LeroymerlinWebsite/v1/navigation-pdp-api/get-characteristics?productId={vendor_code}&regionCode="
            raw_charactiristics = requests.get(url, headers=self.headers).json()
            сharacteristics = []
            for item in raw_charactiristics.get("characteristics"):
                key = list(item.keys())[0]
                value = item[key]
                сharacteristics.append(Characteristic(value='\n'.join(value['value']), description=value['description']))
        except Exception:
            raise RuntimeError("ошибка получения характеристик")
        return сharacteristics
    
    def _get_photos(self, vendor_code: int) -> List[str]:
        try:
            url = self.base_api_url + f"experience/LeroymerlinWebsite/v1/navigation-pdp-api/get-product-media?productId={vendor_code}&regionCode="
            raw_photos = requests.get(url, headers=self.headers).json()
            photos = [item.get("url") for item in raw_photos.get("images")]
        except Exception:
            raise RuntimeError("не удалось получить фотографии(")
        print(photos)
        return photos
    
    def _get_product_main_info_from_api(self, vendor_code: int) -> Dict:
        url = self.base_api_url + f"experience/LeroymerlinWebsite/v1/navigation-pdp-api/get-product-main-info?productId={vendor_code}&regionCode="
        try:
            raw_product_info = requests.get(url, headers=self.headers)
            if raw_product_info.status_code != 200:
                raise Exception
        except Exception:
            raise RuntimeError("ошибка получения информации о товаре из api")
        return raw_product_info.json()

    def get_product_information(self, product_url) -> Product:
        vendor_code = self._get_vendor_code(product_url)
        raw_product_info = self._get_product_main_info_from_api(vendor_code)

        return Product(
            url=product_url,
            vendor_code=vendor_code,
            name=self._get_name(raw_product_info),
            price=self._get_price(raw_product_info),
            rating=random.randrange(1, 5),
            description=self._get_description(raw_product_info),
            сharacteristics=self._get_сharacteristics(vendor_code),
            photos=self._get_photos(vendor_code)
        )
            

class Parser(BaseParser):
    ...