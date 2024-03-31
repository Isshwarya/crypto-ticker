# Database design

Both SQL and noSQL databases were contenders. Finally postgrSQL (a SQL database) was selected as the concerned data is well structured.

## Tables

### CryptoPrice

This table captures price of every cryptocurrency pair (or symbol) for every capture interval unit of time.
Applications like TickerTape, TradingView stores data of stocks/cryptocurrencies every minute. But just for demonstration, we are storing data for every second. But in realtime, storing data per minute would make sense depending on product requirements.

The table is partitioned to allow for efficient filtering of data for historical analysis. We used weekly partitions and currently partitions are manually defined for the ongoing month. The DB procedure "create_partitions" is defined to create the partition and this can be automated with the help of cronjob or other schedulers to create partitions automatically before the beginning of every month. If required, the parition design allows us to efficiently drop very old data without affecting the database performance.

### LatestCryptoPrice

This table stores one record for every supported cryptocurrency pair and tracks the latest price of it. Having a separate table would greatly improve the performance of current_price API.

### Settings

This table stores any application specific global settings
