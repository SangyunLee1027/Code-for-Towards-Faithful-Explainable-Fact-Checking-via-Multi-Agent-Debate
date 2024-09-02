import pandas as pd
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
def response_API_chain_of_thought(sample, sample_output, input_, myKwargs = {}):
    
    try:
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
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are profesional annotator."},
                {"role": "user", "content": """Give me the error types that generated explanation can contain."""},
                {"role": "assistant", "content": error_type},
                {"role": "user", "content": f"""{sample}"""},
                {"role": "assistant", "content": f"""{sample_output}"""},
                {"role": "user", "content": f"""{input_}"""},
            ]
        )  
    
    except openai.error.APIConnectionError:
        print("Failed")
    except openai.error.InvalidRequestError:
        print("InvalidRequestError Failed")
        return None
    
    return response['choices'][0]['message']['content']


def CoT(df):

    def format_prompt(idx):
        return ("Claim: " + df["claim"][idx] +"\n\n" + "annotated_label: " + df["label"][idx] + "\n\n" + "Source: " + df["evidence"][idx] + "\n \n" + "Can you provide an detail explanation that supports the annotated_label {True, False, Half-True} of the claim?")

    sample = """Claim: The builder of Shadow Creek Golf Course is an Arab real estate developer. The builder also owns the Encore hotel and casino in the town where Carolyn Goodman (politician) is mayor.
    label: false
    Source: adow Creek is an 18-hole golf course in North Las Vegas, Nevada, designed by Tom Fazio and built by Las Vegas casino magnate Steve Wynn in 1989.
    Encore Las Vegas (also called Encore at Wynn Las Vegas; often just called Encore) is a luxury resort, casino and hotel located on the Las Vegas Strip in Paradise, Nevada. The resort is connected to its sister resort, Wynn Las Vegas; both are owned by Wynn Resorts, headed by casino developer Steve Wynn.
    Stephen Alan Wynn ("né" Weinberg; born January 27, 1942) is an American real estate businessman and art collector. He is known for his involvement in the American luxury casino and hotel industry. Early in his career he oversaw the construction and operation of several notable Las Vegas and Atlantic City hotels, including the Golden Nugget, the Golden Nugget Atlantic City, The Mirage, Treasure Island, the Bellagio, and Beau Rivage in Mississippi, and he played a pivotal role in the resurgence and expansion of the Las Vegas Strip in the 1990s. In 2000, Wynn sold his company Mirage Resorts to MGM Grand Inc., resulting in the formation of MGM Mirage (now MGM Resorts International). Wynn afterwards took his company Wynn Resorts public in an initial public offering, and he remains Wynn Resorts' CEO and Chairman of the Board. He is a member of the Republican Party. Wynn is the finance chair of the Republican National Committee (RNC) since 2017.
    Carolyn Goldmark Goodman (born March 25, 1939) is an American politician. She has been the mayor of Las Vegas, Nevada since 2011. She is the wife of former mayor and attorney Oscar Goodman, and the second female mayor of Las Vega
    
    Can you provide an detail explanation that supports the annotated_label {True, False, Half-True} of the claim?"""

    sample_answer = """The claim that the video shows Greta Thunberg firing a rifle is false. The video in question was uploaded to YouTube with the title "Greta Thunberg fires rifle," leading some users to believe that it shows the climate change activist. However, an investigation using a reverse image search revealed that the person in the video is actually Emmy Slinge, a 31-year-old markswoman from Stockholm.

    Emmy Slinge had posted a video of herself shooting a rifle on December 7th, which led to her being mistaken for Greta Thunberg. The video of Slinge was then mislabeled as showing Thunberg in the YouTube video.

    It is important to note that Thunberg has been a target of online misinformation and conspiracy theories, with false information and doctored images of her circulating on social media. This false claim about the video showing Thunberg firing a rifle adds to the ongoing misinformation targeted at her.

    Therefore, based on the evidence provided, it can be concluded that the claim is false."""

    for i in range(len(df)):
        prompt = format_prompt(i)
        prediction = response_API_chain_of_thought(sample, sample_answer, prompt)
        df["CoT"][i] = prediction

    return df
