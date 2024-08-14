import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from app.db import engine, create_db_and_tables, PredictionsTickets
from app.utils import preprocessing_fn
from sqlmodel import Session, select
from enum import Enum

#Create the app
app = FastAPI(title="FastAPI, Docker, and Traefik")

#set global variable, the dicctionary to reference mapping the labels
global label_mapping

label_mapping = {
    "0": "Bank Account Services",
    "1": "Credit Report or Prepaid Card",
    "2": "Mortgage/Loan"}

# define data structure for each input 
class Sentence(BaseModel):
    client_name: str
    text: str 

# define data structure for request, a list becasue is loaded by batches, so there will be several entries. 
class ProcessTextRequestModel(BaseModel):
    sentences: list[Sentence]

#entrypoint
@app.post("/predict")
async def read_root(data: ProcessTextRequestModel):

    #Start eh session in the data base
    session = Session(engine)
    
    #Read the model using joblib
    model = joblib.load("model.pkl")

    preds_list = []
    
    #Now we process the entry data
    for sentence in data.sentences: 
        processed_data_vectorized = preprocessing_fn(sentence.text)
        X_dense = [sparse_matrix.toarray() for sparse_matrix in processed_data_vectorized]
        X_dense = np.vstack(X_dense) 

        preds = model.predict(X_dense)
        decoded_predictions = label_mapping[str(preds[0])]

        # create object with predictions
        prediction_ticket = PredictionsTickets(
            client_name=sentence.client_name,
            prediction=decoded_predictions
        )
        
        print(prediction_ticket)

        preds_list.append({
            "client_name": sentence.client_name,
            "prediction": decoded_predictions
        })
        
        session.add(prediction_ticket)

    session.commit() # bulk
    session.close()

    return {"predictions": preds_list}


#initial event of app - db initialization 
@app.on_event("startup")
async def startup():
    create_db_and_tables()
