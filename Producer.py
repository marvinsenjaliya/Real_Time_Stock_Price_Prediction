from time import sleep
from kafka import KafkaProducer
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import sys
import random
import json

def take_data():
    ticker = 'GOOGL'
    lines = open('alphavintgekeys').read().splitlines()
    keys = random.choice(lines)
    time = TimeSeries(key=keys,output_format='json')
    data , metadata = time.get_intraday(symbol= ticker,interval='1min',outputsize='full')
    return data

def publish_message(producerkey,key,data_key):
    from json import dumps
    key_bytes = bytes(key, encoding='utf-8')
    producerkey.send("stock",json.dumps(data[key]).encode('utf-8'),key_bytes)
    print("message published")
    
def kafka_producer_connection():
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    return producer


if __name__=="__main__":
    data = take_data()
    if len(data) > 0:
        kafka_producer = kafka_producer_connection()
        for key in sorted(data):
            publish_message( kafka_producer,key, data[key])
            sleep(3)
