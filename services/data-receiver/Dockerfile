FROM python:3.8

LABEL MAINTAINER "Isshwarya"

RUN apt-get update && apt-get install -y git unzip

RUN git clone https://github.com/Isshwarya/WordProcessor.git

WORKDIR /WordProcessor

ADD ./data/downloaded_files.zip /WordProcessor/data/downloaded_files.zip

RUN pip install -r requirements.txt

CMD ["sh", "-c", "if [ ! -d ./data/downloaded_files ]; then unzip /WordProcessor/data/downloaded_files.zip -d /WordProcessor/data/; fi && export PYTHONPATH=. && python ./scripts/word_analyzer.py"]