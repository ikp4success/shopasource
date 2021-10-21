# API Usage

#### HEADERS ####
* x-api-key: {API_KEY}

#### GET /api/public_api_key ####
* Returns current public api key.
* Api key might change, and it's limited.
* Usage of api, after max is reset.

#### GET /api/shop/search?sk={keyword}&smatch={match_accuracy}&shl=true&slh=false&shops={shop_name}&async=1 ####
* Match Accuracy - refine results based on keyword
* SHL - High to low
* SLH - Low to High
* Shops - Shop Name, single shops /api/shop/search?sk=wallet&smatch=8&shl=true&slh=false&shops=AMAZON&async=1
* Shops - Shop Name, multiple shops /api/shop/search?sk=wallet&smatch=8&shl=true&slh=false&shops=AMAZON,TARGET&async=1
* Keyword - search keyword
* Async - 1 schedule result and assign to a job id (default).
* Async - 0 wait for result, not recommended. Great for debuging.

#### GET /api/get_result?job_id={job_id} ####
* Job Id - job id from scheduled result above i.e /shop/search

#### GET /api/get_result?job_id={job_id} ####
* Get's list of shops available
