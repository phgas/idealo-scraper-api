import requests
import json


class Scraper:
    REGIONS = {
        'AT': 2,
        'DE': 1,
        'ES': 11,
        'FR': 4,
        'IT': 10,
        'UK': 3
    }

    links = []

    def __init__(self, region):
        if region not in self.REGIONS:
            raise ValueError(
                f"Invalid region '{region}'. Valid regions are {', '.join(self.REGIONS.keys())}.")

        self.siteID = self.REGIONS[region]
        self.region = region
        self.is_payload_valid = None
        self.validation_msg = None

    def validate_payload(self, data):
        self.is_payload_valid = True
        self.validation_msg = ''
        if not isinstance(data.get('limit'), int) or data.get('limit') not in range(1, 101):
            self.is_payload_valid = False
            self.validation_msg = 'limit must be Integer between 1-100'
            return
        if not isinstance(data.get('minPrice'), int):
            self.is_payload_valid = False
            self.validation_msg = 'minPrice must be Integer'
            return
        if not isinstance(data.get('maxPrice'), int):
            self.is_payload_valid = False
            self.validation_msg = 'maxPrice must be Integer'
            return
        include_categories = data.get('includeCategories', [])
        if not isinstance(include_categories, list) or not all(isinstance(i, str) for i in include_categories):
            self.is_payload_valid = False
            self.validation_msg = 'includeCategories must be List of Strings'
            return
        if not isinstance(data.get('sort'), str):
            self.is_payload_valid = False
            self.validation_msg = 'sort must be String'
            return

    def build_payload(self, limit, minPrice, maxPrice, includeCategories, sort):
        payload = json.dumps({
            "operationName": "Search",
            "query": "query Search($siteID: Long!, $query: String!, $offset: Int!, $limit: Int!, $sort: SortType!, $reverse: Boolean!, $filters: SearchFiltersInput, $includeCategoryHits: Boolean!, $includeManufacturerHits: Boolean!, $includeSearchFilterGroups: Boolean!, $includeItemStateHits: Boolean!) {\n  search(\n    siteId: $siteID\n    query: $query\n    offset: $offset\n    limit: $limit\n    sort: $sort\n    reverse: $reverse\n    filters: $filters\n  ) {\n       count\n       categoryHits @include(if: $includeCategoryHits) {\n            categoryId\n      categoryName\n      categoryType\n      amount\n    }\n   \n    manufacturerHits @include(if: $includeManufacturerHits) {\n            manufacturerId\n      searchFilterId\n      manufacturerName\n      searchFilterId\n      amount\n    }\n    searchFilterGroups @include(if: $includeSearchFilterGroups) {\n            name\n      attributeId\n      combinationStrategy\n      orderPos\n      filters {\n                amount\n        orderPos\n        filterId\n        content\n        categoryId\n        ownClicks\n        productClicks\n      }\n    }\n    itemStateHits @include(if: $includeItemStateHits) {\n            itemState\n      amount\n    }\n        items {\n            ...searchItemFields\n    }\n    queryUsed {\n            query\n      filters {\n                minPrice\n        maxPrice\n        availableOnly\n        bargainsOnly\n        excludeUsed\n        includeCategories\n        includeSearchFilters\n        includeManufacturers\n        promotedShops\n        disableModifiers\n      }\n    }\n  }\n}\nfragment searchItemFields on Item {\n    ...itemFields\n    url\n  \n  \n        \n}\nfragment itemFields on Item {\n    itemId\n    name\n   images {\n            images350x350\n  }\n \n} ",
            "variables": {
                "filters": {
                    "bargainsOnly": True,
                    "disableModifiers": ["DELPHI"],
                    "includeCategories": includeCategories,
                    "maxPrice": maxPrice * 100,
                    "minPrice": minPrice * 100,
                    "promotedShops": []
                },
                "includeCategoryHits": False,
                "includeItemStateHits": False,
                "includeManufacturerHits": False,
                "includeSearchFilterGroups": False,
                "limit": limit,
                "offset": 0,
                "query": "",
                "reverse": False,
                "siteID": self.siteID,
                "sort": sort
            }
        })
        return payload

    def fetch(self, limit, minPrice, maxPrice, includeCategories, sort):
        '''
        Validates the payload before fetching the response body. 
        '''
        self.validate_payload({
            "limit": limit,
            "minPrice": minPrice,
            "maxPrice": maxPrice,
            "includeCategories": includeCategories,
            "sort": sort
        })
        if not self.is_payload_valid:
            print(f"Payload validation failed: {self.validation_msg}")
        else:
            payload = self.build_payload(
                limit, minPrice, maxPrice, includeCategories, sort)
            response = requests.post("https://app.idealo.de/app-backend/api", headers={
                                     'Content-Type': 'application/json'}, data=payload)
            content = response.json()

            if response.status_code == 200 and len(content['errors']) == 0:
                items = content['data']['search']['items']
                print(f"Scraped item count: {len(items)}")
                self.links.append(items)
            else:
                print(f'Error scraping count.')


if __name__ == '__main__':

    sample_data = {
        "limit": 10,
        "minPrice": 10,
        "maxPrice": 2000,
        "includeCategories": ["3686"],
        "sort": "RELEVANCE"
    }

    AT_Scraper = Scraper(region="AT")
    AT_Scraper.fetch(**sample_data)
    print(AT_Scraper.is_payload_valid,
          AT_Scraper.validation_msg, AT_Scraper.links)
