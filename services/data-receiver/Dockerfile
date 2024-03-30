FROM python:3.8

LABEL MAINTAINER "Isshwarya"

RUN git clone https://github.com/Isshwarya/crypto-ticker.git

WORKDIR /crypto-ticker

RUN pip install -r /crypto-ticker/services/data-receiver/requirements.txt

CMD ["sh", "-c", "git pull && export PYTHONPATH=. && python /crypto-ticker/services/data-receiver/binance_websock.py -k $BINANCE_API_KEY -s $BINANCE_API_SECRET -d -n $POSTGRES_NAME -u $POSTGRES_USER -p $POSTGRES_PASSWORD"]