# crypto-ticker

To establish a real-time connection to the Binance WebSocket to capture and process the prices of selected cryptocurrencies. Must store the captured price data and offer an API endpoints for users to access current prices, historical data, and perform basic statistical analysis on these data.

## Assumptions

- The problem statement specifically asks for subscribing data from 'trade' WebSocket streams of Binance. Otherwise Kline streams can be used to get single datapoint for the required time interval. For the same symbol, 'trade' streams return multiple entries within a single second and storing all these data will take too much space. So the data-receiver service which is responsible for capturing the data, exposes a command line parameter for this data capture interval. Typically applications like TickerTape, TradingView provides price data for the granularity of minute and so the default is set to 60 seconds. Nevertheless, for the purpose of demonstration, deployment/docker-compose.yml uses DATA_CAPTURING_INTERVAL=1 (which means 1 second) in ENV for data_receiver service. Based on product requirements, tune this accordingly.

## TODOs

- Creation of new partitions should be automated for every week. The necessary stored procedures are already defined and for the month of April 2024, the weekly partitons and listed in initialization DDL file. This is just a quick fix solution in the interest of time. This will not scale. This can be automated by using a cron job which invokes the stored procedure in DB by specifying timestamp ranges. Or the data-receiver service can periodically check what partitions currently exist and create new weekly partitions as needed before every month starts.
