import pandas as pd
import openai
import backoff
from openai.error import RateLimitError
from glob import glob
import json
import os
from tqdm import tqdm
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
def response_API(chat_log, myKwargs = {}):
   
    try:
        response = openai.ChatCompletion.create(
        # model="gpt-4-turbo-preview",
        model="gpt-3.5-turbo-16k",
        # model = "gpt-4",
        messages=[
                {"role": "system", "content": "You are profesional annotator."},
                # {"role": "user", "content": ""}
                # {"role": "assistant", "content": ""},
            ] + chat_log
        )   
        
    except openai.error.APIConnectionError:
        print("Failed")
    except openai.error.InvalidRequestError:
        print("InvalidRequestError Failed")
        return None
    
    return response['choices'][0]['message']['content']


def debate(df):
    for i in range(len(df)):
        df["Debate"][i] = debation(i)[0][-1]["content"]

    def debation(idx, iteration = 2):
        input_d_1 = format_prompt(idx)
        input_d_2 = format_prompt(idx)
        debator_1_log = [{"role": "user", "content": f"""{input_d_1} """}]
        debator_2_log = [{"role": "user", "content": f"""{input_d_2} """}]

        debator_1_response = response_API(debator_1_log)
        debator_2_response = response_API(debator_2_log)

        debator_1_log.append({"role": "assistant", "content": f"""{debator_1_response}"""})
        debator_2_log.append({"role": "assistant", "content": f"""{debator_2_response}"""})

        for i in range(iteration):
            input_d_1 = format_prompt_for_debate(debator_2_log[-1]["content"])
            input_d_2 = format_prompt_for_debate(debator_1_log[-1]["content"])

            debator_1_log.append({"role": "user", "content": f"""{input_d_1} """})
            debator_2_log.append({"role": "user", "content": f"""{input_d_2} """})

            debator_1_response = response_API(debator_1_log)
            debator_2_response = response_API(debator_2_log)

            debator_1_log.append({"role": "assistant", "content": f"""{debator_1_response}"""})
            debator_2_log.append({"role": "assistant", "content": f"""{debator_2_response}"""})

        return debator_1_log, debator_2_log

    def format_prompt(idx):
        return "Claim: " + df["claim"][idx] +"\n\n" + "annotated_label: " + df["label"][idx] + "\n\n" + "Source: " + df["evidence"][idx] + "\n \n" + "Can you provide an detail explanation that supports the annotated_label {True, False, Half-True} of the claim?"
    
    def format_prompt_for_debate(other_agent_response):
        return """Here is the fact checking explanation given by other agents: <{other_agent_response}>. Closely examine your explanation and explanation of other agents and provide an updated explanation."""