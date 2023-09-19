# django-rest

This repository hosts a Django API that scrapes data from the Idealo backend based on given parameters. The API also includes rate-limiting and API Key authentication. It serves different endpoints to fetch data and to generate API keys.

## Table of Contents

- [Prerequisites](#Prerequisites)
- [Installation](#Installation)
- [Usage](#Usage)
  - [Endpoints](#Endpoints)
  - [Example Request Body](#Example-Request-Body)
  - [Example Response Body](#Example-Response-Body)
- [API Key Management](#API-Key-Management)
- [Rate Limiting](#Rate-Limiting)
- [Status Codes](#Status-Codes)

## Prerequisites

- Python 3.8
- pip
- SQLite (or any other relational database)

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/phgas/django-rest.git
    ```
2. Navigate into the project directory:
    ```bash
    cd django-rest
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4. Navigate into the project directory:
    ```bash
    cd idealo_project
    ```
5. Migrate the database:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## Usage

Run the Django development server:
```bash
python manage.py runserver
```

### Endpoints

- `GET /data/idealo/<str:region>`: Fetches data from Idealo based on the given region. Valid options are AT, DE, ES, FR, IT, and UK.
- `POST /data/idealo`: Fetches data from Idealo based on the request body. Requires an API Key.
- `POST /generate_key`: Generates an API key. IP address restricted and requires an authorization header.
- `GET /`: A simple landing page.

#### Example Request Body

Here is an example of a request body for the POST endpoint `/data/idealo`:

```json
{
    "limit": 10,
    "minPrice": 10,
    "maxPrice": 2000,
    "includeCategories": [
        "30311"
    ],
    "sort": "RELEVANCE",
    "region": "DE"
}
```

- **limit**: The number of search results to be returned. Must be an integer between `1` and `100`.
- **minPrice**: The minimum price filter for the search query, represented in euros.
- **maxPrice**: The maximum price filter for the search query, represented in euros.
- **includeCategories**: A list of category IDs to filter the search by. For example, the ID `30311` corresponds to electronics: [Idealo Electronics Category](https://www.idealo.de/preisvergleich/SubProductCategory/30311.html).
- **sort**: Specifies the sort order for the search results. Valid options are `RELEVANCE`, `DISCOUNT`, and `LISTED_SINCE`.
- **region**: The region where you want to perform the search. Valid options are `AT`, `DE`, `ES`, `FR`, `IT`, and `UK`.

#### Example Response Body

Here is an example of a response body for the POST request to `/data/idealo`:

```json
{
    "success": true,
    "processing_time_ms": 163.01,
    "data": [
        {
            "itemId": "203192338",
            "name": "Makita DDF486RMJ",
            "images": {
                "images350x350": [
                    "https://cdn.idealo.com/folder/Product/203192/3/203192338/s2_produktbild_mid/makita-ddf486rmj.jpg",
                    ...
                ]
            },
            "url": "https://www.idealo.at/preisvergleich/OffersOfProduct/203192338_-ddf486rmj-makita.html"
        },
        ...
    ]
}
```

- **success**: A boolean value indicating if the request was successful.
- **processing_time_ms**: The time it took to process the request in milliseconds.
- **data**: An array containing the search results, each as an object with the following keys:
    - **itemId**: A unique identifier for the item.
    - **name**: The name of the item.
    - **images**: An object containing a key `images350x350` which is an array of URLs to images of the item with a resolution of 350x350 pixels.
    - **url**: The URL for more details or to purchase the item.

## API Key Management

To generate an API key, make a POST request to the `/generate_key` endpoint. This endpoint is IP restricted and requires an Authorization header with a `SECRET_KEY`. In this case, only the localhost is allowed to generate API keys.

Here is an example of a request body:

```json
{
    "email": "example@example.com",
    "subscription_type": "premium"
}
```

- **email**: The email address where you want to receive the API key or associate with the API key.
- **subscription_type**: The type of API subscription you are interested in. Valid options are `free` (1000 requests), `basic` (5000 requests), and `premium` (10000 requests).

You would also need to include the `Authorization` header containing the `SECRET_KEY` in your POST request.

With this request body, the server will validate the email and the subscription type, then generate an API key accordingly if no errors are encountered.
## Rate Limiting

The rate-limiting is implemented based on the `subscription_type` linked to the API key.

In addition to the custom rate-limiting based on `subscription_type`, this API also utilizes Django's built-in throttling mechanisms. Django provides a variety of ways to throttle requests, including:

- **AnonRateThrottle**: Throttling for anonymous requests.
- **UserRateThrottle**: Throttling based on authenticated user.
- **ScopedRateThrottle**: Allows for custom-defined throttling scopes and rates.

You can configure these in your `settings.py` to better manage request rates. For more information on how to implement and customize throttling in Django, refer to the [official documentation](https://www.django-rest-framework.org/api-guide/throttling/).

## Status Codes

- 200: Success
- 400: Bad Request
- 401: Unauthorized (API Key errors)
- 415: Unsupported Media Type (non-JSON requests)
- 429: Too Many Requests (rate-limiting)
- 500: Internal Server Error
