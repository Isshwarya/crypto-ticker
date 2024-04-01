# crypto-ticker

To establish a real-time connection to the Binance WebSocket to capture and process the prices of selected cryptocurrencies. Must store the captured price data and offer an API endpoints for users to access current prices, historical data, and perform basic statistical analysis on these data.

## Assumptions

- The problem statement specifically asks for subscribing data from 'trade' WebSocket streams of Binance. Otherwise Kline streams can be used to get single datapoint for the required time interval. For the same symbol, 'trade' streams return multiple entries within a single second and storing all these data will take too much space. So the data-receiver service which is responsible for capturing the data, exposes a command line parameter for this data capture interval. Typically applications like TickerTape, TradingView provides price data for the granularity of minute and so the default is set to 60 seconds. Nevertheless, for the purpose of demonstration, deployment/docker-compose.yml uses DATA_CAPTURING_INTERVAL=1 (which means 1 second) in ENV for data_receiver service. Based on product requirements, tune this accordingly.

## Solution details

This applications collects data for symbols: BNBBTC,BTCUSDT,ETHUSDT by default. This can be customized by specifying different symbols to "SYMBOLS" ENV in deployment/docker-compose.yml.

### Documentation

https://documenter.getpostman.com/view/18970982/2sA35HVzs2

### Deployment

Simply deploy the containers using docker-compose. It will deploy the db, initialize the db, start the data collection script (data_receiver service) and the webserver which serves the REST APIs.

First, install docker-compose

```console
pip install docker-compose
```

Second, pull the necessary images from Dockerhub using

```console
>>> docker pull isshwarya/crypto_ticker:latest
>>> docker pull isshwarya/data_receiver_service:latest
```

Finally, instantiate the containers

```console
>> cd crypto-ticker
>> docker-compose -f deployment/docker-compose.yml up -d
```

This will deploy all the three containers.

Allow these containers to run for few minutes atleast so that enough data gets collected for tracking crypto prices. Then remember to use this datatime range for API requests

Additionally for admin purposes:

- At this point, super user account with username=admin has been created for the django application.

- Go to "http://0.0.0.0:8020/admin" in the browser and login as the created superuser (We use username:admin, password:admin. This can be changed in docker-compose.yml file as needed).

### Example APIs

#### Current Price

```console
http://0.0.0.0:8020/api/current_price/?symbol=BTCUSDT
```

#### Historical Price (List Prices)

```console
http://0.0.0.0:8020/api/crypto_price/?symbol=BTCUSDT&start_datetime=2024-03-31T21:53:27&end_datetime=2024-03-31T22:16:29
```

#### Statistics

```console
http://0.0.0.0:8020/api/crypto_price/statistics/?symbol=BTCUSDT&start_datetime=2024-03-31T21:53:27&end_datetime=2024-03-31T22:16:29
```

NOTE: Depending on where you deployed the webserver and where you are executing the APIs, adjust the hostname
(0.0.0.0) in the url accordingly.

### How to run the tests

The unit test cases can be executed as:

Install all the requirements at crypto-ticker/webserver/requirements.txt either globally or in a virtual environment (recommended). Then run:

```console
>>> cd crypto-ticker/webserver/cryptoticker
>>> python manage.py test
```

## TODOs

- Creation of new partitions should be automated for every week. The necessary stored procedures are already defined and for the month of April 2024, the weekly partitons and listed in initialization DDL file. This is just a quick fix solution in the interest of time. This will not scale. This can be automated by using a cron job which invokes the stored procedure in DB by specifying timestamp ranges. Or the data-receiver service can periodically check what partitions currently exist and create new weekly partitions as needed before every month starts.

- Documentation for internal methods all throughout the code.
