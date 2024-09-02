import pandas as pd
import ast


import openai
import backoff
from openai.error import RateLimitError
from glob import glob
import json
import os
import pandas as pd
from tqdm import tqdm

openai.organization = ""
openai.api_key = ""

@backoff.on_exception(backoff.expo, RateLimitError)
def response_API(prompt, myKwargs = {}):
   
    try:
        response = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        # model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are profesional annotator."},
                {"role": "user", "content": f"""{prompt} """},
                
            ]
        )   
        
    except openai.error.APIConnectionError:
        print("Failed")
    except openai.error.InvalidRequestError:
        print("InvalidRequestError Failed")
        return None
    
    return response['choices'][0]['message']['content']

def vanilla(df):

    def format_prompt(idx):
        
        return "Claim: " + df["claim"][idx] +"\n\n" + "annotated_label: " + df["label"][idx] + "\n\n" + "Source: " + df["evidence"][idx] + "\n \n" + "Can you provide an detail explanation that supports the annotated_label {True, False, Half-True} of the claim?"

    for i in range(len(df)):
        prompt = format_prompt(i)
        prediction = response_API(prompt)
        df["vanilla"][i] = prediction
    
    return df

