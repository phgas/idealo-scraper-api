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

    def __init__(self):
        self.siteID = None
        self.region = None

    def validate_payload(self, data):
        if isinstance(data.get('limit'), int) == False or data.get('limit') not in range(1, 101):
            return False, 'limit must be Integer between 1-100'
        if isinstance(data.get('minPrice'), int) == False:
            return False, 'minPrice must be Integer'
        if isinstance(data.get('maxPrice'), int) == False:
            return False, 'maxPrice must be Integer'
        if isinstance(data.get('includeCategories'), list) == False or all(isinstance(i, str) for i in data.get('includeCategories')) == False:
            return False, 'includeCategories must be List of Strings'
        if isinstance(data.get('sort'), str) == False:
            return False, 'sort must be String'
        if isinstance(data.get('region'), str) == False or data.get('region') not in self.REGIONS:
            return False, f"region must be String. Valid regions are {', '.join(self.REGIONS.keys())}."
        return True, ''

    def build_payload(self, limit, minPrice, maxPrice, includeCategories, sort, region):
        self.siteID = self.REGIONS.get(region)
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

    def fetch(self, limit, minPrice, maxPrice, includeCategories, sort, region):
        '''
        Validates the payload before fetching the response body. 
        '''
        is_payload_valid, validation_msg = self.validate_payload({
            "limit": limit,
            "minPrice": minPrice,
            "maxPrice": maxPrice,
            "includeCategories": includeCategories,
            "sort": sort,
            "region": region
        })

        if not is_payload_valid:
            print(f"Payload validation failed: {validation_msg}")
            return is_payload_valid, validation_msg, None

        payload = self.build_payload(
            limit, minPrice, maxPrice, includeCategories, sort, region)
        response = requests.post("https://app.idealo.de/app-backend/api",
                                 headers={'Content-Type': 'application/json'}, data=payload)
        content = response.json()

        if response.status_code == 200 and len(content['errors']) == 0:
            items = content['data']['search']['items']
            print(f"Scraped item count: {len(items)}")
            return is_payload_valid, validation_msg, items
        else:
            print(f'Error scraping count.')
            return is_payload_valid, "Error scraping count.", None


if __name__ == '__main__':

    sample_data = {
        "limit": 10,
        "minPrice": 10,
        "maxPrice": 2000,
        "includeCategories": ["3686"],
        "sort": "RELEVANCE",
        "region": "AT"
    }

    print(Scraper().fetch(**sample_data))
