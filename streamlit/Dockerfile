FROM python:3.9-slim

WORKDIR /usr/src/app

RUN rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get upgrade -y
RUN apt-get install graphviz git dos2unix unzip curl -y

COPY utils/ ./utils/
COPY pages/ ./pages/
COPY images/ ./images/
COPY data/ ./data/
COPY .streamlit/ ./.streamlit/
COPY *.txt .
COPY *.py .
COPY *.jpg .
COPY *.yml .

RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]