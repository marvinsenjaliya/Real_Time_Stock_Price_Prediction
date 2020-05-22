import json
import time
import pandas as pd

from datetime import datetime
from flask import Flask, render_template, make_response

from pyspark import SparkContext
from pyspark.sql import SQLContext
from kafka import KafkaConsumer
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegressionModel
from pyspark.sql.types import DoubleType

# creating spark context
sc = SparkContext(appName="StockPricePrediction")
sqlContext = SQLContext(sc)


vectorAssembler = VectorAssembler(inputCols=['open', 'high', 'low'], outputCol='features')
Model_Path =  "/home/hadoopmarvin1/kafka_2.11-0.9.0.0/bin/my_model/"
load_model = LinearRegressionModel.load(Model_Path)


from kafka import KafkaConsumer
from json import loads
import pandas as pd
import json
consumer  = KafkaConsumer('stock')
def stock_price_prediction(load_model):
    consumer  = KafkaConsumer('stock')
    for message in consumer:
    #print(type(message.value))
        res_dict = json.loads(message.value.decode('utf-8'))
        data_list = list(res_dict.values())
        dataframe = pd.DataFrame([data_list], columns=['Open','Close','Volume','High','Low'])
        spark_dataframe = sqlContext.createDataFrame(dataframe)
        spark_Dataframe = spark_dataframe.selectExpr("cast(High as double) Volume",
                                   "cast(Open as double) Open",
                                   "cast(Low as double) Low",
                                    "cast(High as double) High",
                                    "cast(Close as double) Close",)
        vectorAssembler = VectorAssembler(inputCols = ['Open','High','Low'], outputCol = 'features')
        spark_Dataframe_vect = vectorAssembler.transform(spark_Dataframe)
        spark_Dataframe_vect_features = spark_Dataframe_vect.select(['features','Close'])
        predictions = load_model.transform(spark_Dataframe_vect_features)
        predictions.select("prediction","Close","features").show()
        predict_value = predictions.select('prediction').collect()[0].__getitem__("prediction") 
        close_value = predictions.select('Close').collect()[0].__getitem__('Close') 
        print(message.key)
        date_time = message.key.decode('utf-8')
        return predict_value , close_value , date_time

stock_price_prediction(load_model)

from flask import Flask, redirect,url_for,render_template,request,make_response
app = Flask(__name__)
@app.route("/")
def hello():
    return "hello this is the home page"

@app.route('/data', methods=['GET', 'POST'])
def data():
    stock_price, close_price, date_time = stock_price_prediction(vectorAssembler, load_model)

    date_time = int(datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').strftime('%s')) * 1000

    data = [date_time, stock_price, close_price]

    response = make_response(json.dumps(data))

    response.content_type = 'application/json'

    time.sleep(2)
    
    return response

if __name__==("__main__"):
    app.run(host="0.0.0.0" , port=8080)
