import pandas as pd
import openai
import backoff
from openai.error import RateLimitError
from glob import glob
import json
import os
import copy
import pandas as pd
from tqdm import tqdm


openai.organization = ""
openai.api_key = ""


@backoff.on_exception(backoff.expo, RateLimitError)
def response_API_gpt_fb_rf(input_, myKwargs = {}):
   
    try:
        
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=input_
        )  
    
    except openai.error.APIConnectionError:
        print("Failed")
    except openai.error.InvalidRequestError:
        print("InvalidRequestError Failed")
        return None
    
    return response['choices'][0]['message']['content']


error_type = """Error definition:
            Intrinsic Entity-Related Errors: Intrinsic entity-related errors occur when there is a mistake in representing named entities, quantities, dates, or other surface realizations from the given source within the generated explanation. Example: Incorrectly combining distinct entities from the given source.
            Extrinsic Entity-Related Errors: Extrinsic entity-related errors involve the introduction of new entities that are not present in the given source into the generated explanation. Example: Hallucinating new entities that do not exist in the source.
            Intrinsic Event-Related Errors: Intrinsic event-related errors pertain to mistakes in representing events mentioned in the generated explanation, leading to incorrect claims about events. Example: Making inaccurate claims about events mentioned in the explanation.
            Extrinsic Event-Related Errors: Extrinsic event-related errors occur when the generated explanation includes new events that are not present in the given source. Example: Introducing fabricated events that are not supported by the source.
            Intrinsic Noun Phrase-Related Errors: Intrinsic noun phrase-related errors are mistakes related to noun phrases, excluding entity-specific errors. They may involve miscombining noun phrases with incorrect modifiers from the given source. Example: Incorrectly combining a noun phrase with the wrong modifier from the source.
            Extrinsic Noun Phrase-Related Errors: Extrinsic noun phrase-related errors involve the introduction of new noun phrase modifiers that are not present in the given source into the generated explanation. Example: Hallucinating new noun phrase modifiers not supported by the source.
            Reasoning Coherence Errors: Reasoning coherence errors occur when there are logical flaws in the flow of reasoning within the generated explanation, leading to a lack of coherence or weak support for the claim. Example: Presenting evidence that does not logically connect to the main claim, resulting in a disjointed explanation.
            Overgeneralization Errors: Overgeneralization errors happen when the generated explanation makes sweeping statements or draws conclusions that go beyond the scope of the evidence provided.
            Irrelevant Evidence Errors: Irrelevant evidence errors occur when the generated explanation includes evidence that is not directly related to the claim, leading to confusion and lack of support for the main argument. Example: Including evidence that is tangential or unrelated to the claim being explained.
        """

base_ = [{"role": "system", "content": "You are profesional annotator."},

    {"role": "user", "content": """Give me the error types that generated explanation can contain."""},
    {"role": "assistant", "content": error_type},
        {"role" : "user", "content" :"""Claim: Says Nancy Pelosi was arrested after ripping a copy of the State of the Union speech.
annotated_label: false
Source: Accompanying an array of images in a recent Facebook post , including photos of civil court filings, screenshots of tweets, and a picture of U.S. House Speaker Nancy Pelosi, is one explosive allegation: that the California Democrat was arrested. This post was flagged as part of Facebook\u2019s efforts to combat false news and misinformation on its News Feed. (Read more about our partnership with Facebook .) There are screenshots of several tweets from one account in the Facebook post, including these: \"BREAKING While leaving the US Capitol nancy Pelosi has been intercepted by US Marshals and ARRESTED (!) under the direct order of President Trump. WH claims ripping up speech was violation of decorum provision of Rule XIX!\" \"Marshals holding Pelosi are NOT(!) allowing her a phone call or to contact her attorneys. Chuck Schumer is racing back to the US capitol. White House sources say that she will be transported to undisclosed location TONIGHT (!) to face MILITARY TRIBUNAL (!!!)\" First of all, Pelosi didn\u2019t break the law when she tore up a copy of President Donald Trump\u2019s State of the Union address on Feb. 4. Trump , among others , wrongly claimed it was illegal. And while some people have signed a Change.org petition calling for her arrest after she ripped up her copy of the president\u2019s speech, no arrest has happened. We found no news coverage online about Pelosi being taken into custody. If she had been arrested, it would have drawn plenty of media attention.
"""},
    {"role" : "assistant", "content":  """Explanation: Nancy Pelosi, the California Democrat, was allegedly arrested after tearing up a copy of the State of the Union speech, according to an explosive statement shared on Facebook. This statement was accompanied by various images like civil court filings, tweets, and a photo of Pelosi. There were also screenshots of tweets from an unidentified account claiming that Pelosi was arrested by US Marshals under President Trump's orders for violating the "decorum provision of Rule XIX" and that she would face a military tribunal.
However, there's no evidence or legal foundation supporting these claims. Firstly, Nancy Pelosi did not break any law by tearing the State of the Union address on February 4. This act was mistakenly said to be illegal by several, including President Donald Trump. Even though a Change.org petition emerged asking for Pelosi's arrest post the incident, she was never actually taken into custody. If she had been arrested, news agencies globally would have reported on it extensively.
"""},
    {"role": "system", "content": "You are a professional analyzer who find potential errors, which might weaken faithfulness, in the generated explanation (not in the source) and categorize them according to predefined error types. Thoroughly comprehend the provided source and the task carefully."},
    {"role" : "user", "content" : """Find all errors(Intrinsic Entity-Related error, Extrinsic Entity-Related error, Intrinsic Event-Related error, Extrinsic Event-Related error, Intrinsic Noun-Phrase-Related error, Extrinsic Noun-Phrase-Related error, reasonability-Related error, Connected evidence related error) in the \"generated explanation\" and provide the feedback by following the steps; Error count: how many errors have been found (what types of error); Step 1) Recognize what type(s) of error has been found in the generated explanation; Step 2) Recognize which sentence(s) contain(s) the error(s); Step 3) Recognize what causes the error; Step 4) Why is the error; Step 5) How the error should be corrected; If there are multiple errors, please write 5 steps for each error."""},
    {"role" : "assistant", "content": """Feedback: 
    Error count: 9
        Error 1:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Intrinsic Entity-Related Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "There were also screenshots of tweets from an unidentified account" 
            Step 3) Why is the error;
                The source mentioned the account but did not label it as "unidentified."
            Step 4) How the error should be corrected;
                "There were also screenshots of several tweets from one account." 
    
        Error 2:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Extrinsic Entity-Related Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "This statement was accompanied by various images like civil court filings"
            Step 3) Why is the error;
                The source did not explicitly mention "various images" accompanying the statement.
            Step 4) How the error should be corrected;
                "This statement was accompanied by images, including photos of civil court filings, screenshots of tweets, and a picture of U.S. House Speaker Nancy Pelosi." 
     
        Error 3:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Intrinsic Event-Related Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "Nancy Pelosi did not break any law by tearing the State of the Union address on February 4."
            Step 3) Why is the error;
                The source specifically mentions she didn't break the law by tearing up the speech, but this sentence makes it sound like the act of tearing was the event.
            Step 4) How the error should be corrected;
                "Nancy Pelosi did not break any law when she tore up a copy of President Donald Trump's State of the Union address on February 4."

        Error 4:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Extrinsic Event-Related Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "Even though a Change.org petition emerged asking for Pelosi's arrest post the incident, she was never actually taken into custody."
            Step 3) Why is the error;
                The Change.org petition emergence and her not being arrested are two separate events. Combining them might suggest a causative relationship.
            Step 4) How the error should be corrected;
                "While some people signed a Change.org petition calling for her arrest after she ripped up the speech, no actual arrest has taken place."
     
        Error 5:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Intrinsic Noun Phrase-Related Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "Nancy Pelosi, the California Democrat, was allegedly arrested after tearing up a copy of the State of the Union speech, according to an explosive statement shared on Facebook." 
            Step 3) Why is the error;
                 "Explosive statement" incorrectly combines the adjective "explosive" with the noun "statement," suggesting a level of drama that wasn't in the original source.
            Step 4) How the error should be corrected;
                "According to a claim shared on Facebook."

        Error 6:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Extrinsic Noun Phrase-Related Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "However, there's no evidence or legal foundation supporting these claims." 
            Step 3) Why is the error;
                Introducing the term "legal foundation" which was not present in the original source.
            Step 4) How the error should be corrected;
                "However, there's no evidence supporting these claims."
     
        Error 7:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Reasoning Coherence Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "If she had been arrested, news agencies globally would have reported on it extensively."
            Step 3) Why is the error;
                This is not a guaranteed consequence of an arrest. Some arrests might go under the radar for various reasons.
            Step 4) How the error should be corrected;
                "If she had been arrested, it would have likely drawn significant media attention."
     
        Error 8:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Overgeneralization Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "This act was mistakenly said to be illegal by several, including President Donald Trump."
            Step 3) Why is the error;
                Suggesting that many people believed it was illegal is an overgeneralization based on the provided source.
            Step 4) How the error should be corrected;
                "President Donald Trump, among others, wrongly claimed it was illegal."
     
        Error 9:
            Step 1) Recognize what type(s) of error has been found in the generated explanation;
                Irrelevant Evidence Errors
            Step 2) List sentences with the errors and indicate what type of error in each setnence;
                "This statement was accompanied by various images like civil court filings, tweets, and a photo of Pelosi."
            Step 3) Why is the error;
                The types of images accompanying the statement are not directly relevant to whether the claim about Pelosi's arrest is true or false.
            Step 4) How the error should be corrected;
                Omit this line entirely or tie its relevance more clearly to the main claim, e.g., "The claim was spread alongside various images, suggesting an attempt to lend credibility to the false assertion."
"""},
    {"role": "system", "content": "You are a professional writer who revises the explanation as given feedback says without any modification other than feedback."},
    {"role" : "user", "content" : "Please revise generated explanation for label on fact-checking using the given feedback without any modification other than feedback says."},
    {"role" : "assistant", "content": """Refined Explanation: According to a claim shared on Facebook, Nancy Pelosi, the U.S. House Speaker, was allegedly arrested after tearing up a copy of the State of the Union speech. The claim was accompanied by images, including photos of civil court filings, screenshots of tweets, and a picture of Pelosi. Screenshots from one account made further allegations, stating Pelosi was arrested by US Marshals under President Trump's orders for supposedly violating the "decorum provision of Rule XIX" and suggesting she would face a military tribunal.

However, there's no evidence supporting these claims. Nancy Pelosi did not break any law when she tore up a copy of President Donald Trump's State of the Union address on February 4. President Donald Trump, among others, wrongly claimed it was illegal. While some people signed a Change.org petition calling for her arrest after the incident, no actual arrest has taken place. If Pelosi had been arrested, it would have likely drawn significant media attention.
"""},
{"role": "system", "content": "You are profesional annotator."},
    ]


def self_refinement(df):

    def feedback(base):
        
        base.append({"role": "system", "content": "You are a professional analyzer who find potential errors, which might weaken faithfulness, in the generated explanation (not in the source) and categorize them according to predefined error types. Thoroughly comprehend the provided source and the task carefully."})
        base.append({"role": "user", "content": """"Find all errors(Intrinsic Entity-Related error, Extrinsic Entity-Related error, Intrinsic Event-Related error, Extrinsic Event-Related error, Intrinsic Noun-Phrase-Related error, Extrinsic Noun-Phrase-Related error, reasonability-Related error, Connected evidence related error) in the \"generated explanation\" and provide the feedback by following the steps; Error count: how many errors have been found (what types of error); Step 1) Recognize what type(s) of error has been found in the generated explanation; Step 2) Recognize which sentence(s) contain(s) the error(s); Step 3) Recognize what causes the error; Step 4) Why is the error; Step 5) How the error should be corrected; If there are multiple errors, please write 5 steps for each error."""})
        
        res = response_API_gpt_fb_rf(base)
        base.append({"role": "assistant", "content": f"""{res}"""})
        return base


    def refinement(base):
        role_refine = "You are a professional writer who revises the explanation as given feedback says without any modification other than feedback."
        quest_refine = "Please revise generated explanation for label on fact-checking using the given feedback without any modification other than feedback says. If there is no error, just give us an original explanation."
        
        base.append({"role": "system", "content": f"""{role_refine}"""})
        base.append({"role": "user", "content": f"""{quest_refine}"""})

        output = response_API_gpt_fb_rf(base)

        base.append({"role": "assistant", "content": f"""{output}"""})

        return base

    def fb_rf(idx, base):
        generated_expl = init_format_prompt(idx)
        base.append({"role": "user", "content": generated_expl})
        base.append({"role": "assistant", "content": df["vanilla"][idx]})
        base = feedback(base)
        base = refinement(base)
        
        df["self_refinement"][idx] = base[-1]["content"]


    def init_format_prompt(idx):
        return ("Claim: " + df["claim"][idx] +"\n\n" + "annotated_label: " + df["label"][idx] + "\n\n" + "Source: " + df["evidence"][idx] + "\n \n" + "Can you provide an detail explanation that supports the annotated_label {True, False, Half-True} of the claim?")

    for i in range(len(df)):
        b = copy.deepcopy(base_)
        fb_rf(i, b)

    return df
