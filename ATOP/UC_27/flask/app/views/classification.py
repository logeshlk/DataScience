from os.path import dirname
from flask_cors import CORS 
from flask import Blueprint
import pandas as pd
clustering = Blueprint('clustering',__name__)
cors = CORS(clustering, resources={r"/*": {"origins": "*"}})
from datetime import date
import joblib
import os
import glob
from app.views import preprocessing
from .. import configs
 

class clusteringClass:
    def __init__(self):
        self.preprocessed=''
        self.original=''
        self.dirName=configs.get("drive").data+configs.get('model').data
        self.folders=['modelPickel','cvPickle','modelVisulizations','TestData']
    @clustering.route('/', methods=['GET','POST'])
    def test():
        print("========================",configs.get("drive").data+configs.get("input").data)

        for col in cluster.folders:
            if not os.path.exists(cluster.dirName+col):
                os.mkdir(cluster.dirName+col)
        return 'test'

    @clustering.route('/training',methods=['GET','POST'])
    def retrainingApi():
        method='training'
        print("=================",configs.get("drive").data+configs.get("input").data)
        result=preprocessing.preprocessing(configs.get("drive").data+configs.get("input").data,method)



        return result

    @clustering.route('/classification/predict/<filename>', methods=['GET','POST'])
    def predictCluster(filename):
        method='predict'
        print("=================",configs.get("drive").data+configs.get("input").data)
        # result=preprocessing.preprocessing(configs.get("drive").data+configs.get("model").data+'/TestData/'+filename+'.csv',method)
        op = preprocessing.model_predict(configs.get("drive").data+configs.get('model').data+'/modelPickel/model.pkl',
        configs.get("drive").data+configs.get("output").data,
        configs.get("drive").data+configs.get("model").data+'/TestData/'+filename+'.csv')
        return op
cluster = clusteringClass()