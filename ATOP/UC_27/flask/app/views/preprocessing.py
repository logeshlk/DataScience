import pandas as pd
import numpy as np
import datetime as dt
from bs4 import BeautifulSoup
import re
import tqdm
import unicodedata
from .. import configs

from datetime import date
import pickle
import glob
import json

from sklearn.feature_extraction.text import CountVectorizer

# Bagging Classifier
from sklearn.ensemble import BaggingClassifier

from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn import preprocessing
from sklearn.model_selection import train_test_split

def data_preprocessing(path,method,cv_path= configs.get("drive").data+configs.get('model').data+'cvPickle\cv_train.pkl'):
    if method =='training' :
        all_files = glob.glob(path + "*.csv")
        all_files=[col.replace('\\','/') for col in all_files]
    #     print(all_files)    
        li = []     
        for filename in all_files:
            df = pd.read_csv(filename,header=0,encoding = "ISO-8859-1")        
            li.append(df)    #drop the duplictes in the dataframes            
        df = pd.concat(li, axis=0).drop_duplicates().reset_index(drop=True)
    else :
        df = pd.read_csv(path, encoding='ISO-8859-1')    


    # df=pd.read_csv(frame,encoding = "ISO-8859-1")
    df['Buckets Items'].fillna('', inplace=True)
    df['Predecessor TestCase ID'].fillna(0, inplace=True)
    df['Successor TestCase ID'].fillna(0, inplace=True)
    df['Test Step Update Date'] = pd.to_datetime(df['Test Step Update Date'])
    df['Step_update_date'] = df['Test Step Update Date'].dt.day
    df['Step_update_month'] = df['Test Step Update Date'].dt.month
    df['Execution Time for test step'] = pd.to_datetime(df['Execution Time for test step'])
    df['exe_date'] = df['Execution Time for test step'].dt.day
    df['exe_month'] = df['Execution Time for test step'].dt.month
    df['exe_hour'] = df['Execution Time for test step'].dt.hour
    df['exe_min'] = df['Execution Time for test step'].dt.minute
    df['exe_sec'] = df['Execution Time for test step'].dt.second
    df['Test Case Update Date'] = pd.to_datetime(df['Test Case Update Date'])
    df['case_update_date'] = df['Test Case Update Date'].dt.day
    df['case_update_month'] = df['Test Case Update Date'].dt.month
    df['Data Sheet Update Date'] = pd.to_datetime(df['Data Sheet Update Date'])
    df['data_update_date'] = df['Data Sheet Update Date'].dt.day
    df['data_update_month'] = df['Data Sheet Update Date'].dt.month
    df['Failure Date for a step'] = pd.to_datetime(df['Failure Date for a step'])
    df['step_failed_date'] = df['Failure Date for a step'].dt.day
    df['step_failed_month'] = df['Failure Date for a step'].dt.month
    df['Failure type- Update Date'] = pd.to_datetime(df['Failure type- Update Date'])
    df['RCA_update_date'] = df['Failure type- Update Date'].dt.day
    df['RCA_update_month'] = df['Failure type- Update Date'].dt.month
    df.drop(columns = {'Execution Time for test step','Test Step Update Date',
                   'Test Case Update Date','Data Sheet Update Date','Failure Date for a step',
                   'Failure type- Update Date', 'Test Run Id'}, inplace=True)    
    df['Exception Name'] = df['Exception Name'].astype('str')
    df1 = cv_conversion(pre_process_corpus(df['Exception Name']),method,cv_path)
        
                
    if method == 'training':
        df['Buckets Items'].replace({"Environment Issue": "Application Issue","Timing Exception": "Application Issue", "Infrastrature Issue": "Data related Issue",
        'Timing Issue' : 'Data related Issue', 'Latency related issue' : 'Application Issue' }, inplace=True)
        data = pd.concat([df1,df], axis=1)
        data['Buckets Items'] = data['Buckets Items'].replace({"Application Issue":0, "Automation Issue":1, "Data related Issue":2})
    else :
        data = pd.concat([df1,df], axis=1)
        
    data.drop(columns={'Exception Name'},inplace=True)
        
             
    #Target Renaming
    data = data.rename(columns={'Buckets Items' : 'FailureReason'})
        
        
    return data
#function to remove html tags
def strip_html_tags(text):
  soup = BeautifulSoup(text, "html.parser")
  [s.extract() for s in soup(['iframe', 'script'])]
  stripped_text = soup.get_text()
  stripped_text = re.sub(r'[\r|\n|\r\n]+', '\n', stripped_text)
  return stripped_text


#function defined to remove unicode data

def remove_accented_chars(text):
  text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
  return text

# lower case and remove special characters\whitespaces

def pre_process_corpus(docs):
  norm_docs = []
  for doc in tqdm.tqdm(docs):
    doc = strip_html_tags(doc)
    doc = doc.translate(doc.maketrans("\n\t\r", "   "))
    doc = doc.lower()
    doc = remove_accented_chars(doc)
    #doc = contractions.fix(doc)
    # lower case and remove special characters\whitespaces
    doc = re.sub(r'[^a-zA-Z0-9\s]', '', doc, re.I|re.A)
    doc = re.sub(' +', ' ', doc)
    doc = doc.strip()
    doc=re.sub('[0-9]', '', doc)
    norm_docs.append(doc)
  
  return norm_docs

def cv_conversion(df,method,cv_path):
    
    if method == 'training':
        cv = CountVectorizer(ngram_range=(1, 1), min_df=0.001, max_df=0.99)
        cv_exception_matrix = cv.fit_transform(df)
        pickle.dump(cv, open(cv_path, 'wb'))
    else:
        cv = pickle.load(open(cv_path,'rb'))
        cv_exception_matrix = cv.transform(df)
        
    
    cv_exception_matrix=cv_exception_matrix.toarray()
    # get all unique words in the corpus
    vocab = cv.get_feature_names()
    # show document feature vectors
    data2=pd.DataFrame(cv_exception_matrix, columns=vocab)
        
    return data2

def preprocessing(path,method):

    print('path--------------------',path)
    print('method--------------------',method)
    if method == "training" :
        df_train = data_preprocessing(path,method)
        status = model_training(df_train )

    return status

def model_training(data, path=configs.get("drive").data+configs.get('model').data+'/modelPickel/model.pkl'):
    x = data.loc[:, data.columns != 'FailureReason']
    y = data['FailureReason']
    train_data, test_data, train_rca, test_rca = train_test_split(x,y, test_size=0.2, random_state=42,stratify=y)
    
    
    # define models and parameters
    model = BaggingClassifier()
    #n_estimators = [i for i in range(2,1000) if any(i % x == 0 for x in [50])]
    n_estimators = [10,100,1000]
    # define grid search
    grid = dict(n_estimators=n_estimators)
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
    grid_search = GridSearchCV(estimator=model, param_grid=grid, n_jobs=-1, cv=cv, scoring='accuracy',error_score=0)
    grid_search.fit(train_data, train_rca)
    grid_result = grid_search.predict(test_data)
    accuracy=accuracy_score(test_rca, grid_result )
    
    print ('Accuracy Score is', accuracy)
    
    model = grid_search.fit(x,y)   

    pickle.dump(model, open(path, 'wb'))  
    
    
    return json.dumps({'Accuracy': accuracy})

def model_predict(mdl_path,output,input):
    
    data = data_preprocessing(input,method='predict')   

    x = data.loc[:, data.columns != 'FailureReason']    
    # load the model from disk
    loaded_model = pickle.load(open(mdl_path,'rb'))
    
    result = loaded_model.predict(x)
    pred_result = pd.DataFrame(result, columns=['FailureReason'])
    filename =output+'pred_result_{}.csv'.format(date.today())
    pred_result.to_csv(filename,index=False)
    pred_result['FailureReason'] = pred_result['FailureReason'].replace({0:'Application Issue',1: 'Automation Issue', 2: 'Data related Issue'})
    ip = pd.read_csv(input,encoding = "ISO-8859-1")
    ip.drop(columns = 'Buckets Items', inplace=True)
    ip = ip.rename(columns={'Test Case ID' : 'TestCaseID',
                            'Failed Steps' : 'FailedSteps',
                            'Exception Name': 'ExceptionName'})
    op = pd.concat([ip,pred_result], axis=1)
    filename =output+'output_{}.csv'.format(date.today())
    op.to_csv(filename,index=False)
    df = pd.DataFrame(op, columns = ['TestCaseID','FailedSteps','ExceptionName','FailureReason'])
    filename=output+'UC_27.json'
    df.to_json(filename,orient='records')    
    return df.to_json(orient='records')