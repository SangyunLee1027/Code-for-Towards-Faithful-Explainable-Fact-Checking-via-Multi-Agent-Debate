import pandas as pd
import openai
import backoff
from openai.error import RateLimitError
from glob import glob
import json
import os
from tqdm import tqdm

openai.organization = ""
openai.api_key = ""


@backoff.on_exception(backoff.expo, RateLimitError)
def response_API(role, input_, myKwargs = {}):
    
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
                {"role": "system", "content": f"""{role}"""},
                {"role": "user", "content": """Give me the error types that generated explanation can contain."""},
                {"role": "assistant", "content": error_type},
                {"role": "user", "content": f"""{input_}"""},
            ]
        )  
    
    except openai.error.APIConnectionError:
        print("Failed")
    except openai.error.InvalidRequestError:
        print("InvalidRequestError Failed")
        return None
    
    return response['choices'][0]['message']['content']


@backoff.on_exception(backoff.expo, RateLimitError)
def response_API_gpt_16k(role, input_, myKwargs = {}):
   
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
                {"role": "system", "content": f"""{role}"""},
                {"role": "user", "content": f"""{input_}"""},
            ]
        )   
    
    except openai.error.APIConnectionError:
        print("Failed")
    except openai.error.InvalidRequestError:
        print("InvalidRequestError Failed")
        return None
    
    return response['choices'][0]['message']['content']




@backoff.on_exception(backoff.expo, RateLimitError)
def response_API_continue(role, inputs, myKwargs = {}):
    
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
        input_msg = [
                {"role": "system", "content": f"""{role}"""},
                {"role": "user", "content": """Give me the error types that generated explanatino can contain."""},
                {"role": "assistant", "content": error_type},
            ]
        for i in inputs: 
            input_msg.append(i)
        
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages= input_msg
        )  
    
    except openai.error.APIConnectionError:
        print("Failed")
    except openai.error.InvalidRequestError:
        print("InvalidRequestError Failed")
        return None
    
    return response['choices'][0]['message']['content']

def madr(df):
    def init_debate(idx):
        role_err_type = "You are a professional analyzer who find potential errors, which might weaken faithfulness, in the generated explanation (not in the source) and categorize them according to predefined error types. Thoroughly comprehend the provided source and the task carefully."
        role_type_err = "You are a professional analyzer who find errors, classified by predefined error types, in the generated explanation (not in the source) and provide feedback for correcting them. Thoroughly comprehend the provided source and the task carefully."
        role_judge = "You are a professional analyzer responsible for assessing whether the feedback from both the first and second professional analyzers aligns. If their feedback matches, return only \"True\". If it does not, return only \"False\"."
        
        quest_err_type = """
    Your task: 
        Step 1: Find all potential errors, which might weaken faithfulness, in the generated explanation (not in the source) and provide exact senteces where the errors are found with quotation.
        Step 2: Categorize them according to predefined error types above. 
        Step 3: Provide specific and actionable feedbacks with instruction how to fix them. Please provide only the feedback, not the revised explanation.
        Remember that explanation can contain multiple same errors."""
        quest_type_err = """
    Your task: 
        Step 1: Find all errors categorized by predefined error types, which undermine the faithfulness of the generated explanation (not in the source) and provide exact senteces where the errors are found with quotation.
        Step 2: Provide specific and actionable feedbacks with instruction how to fix them. Please provide only the feedback, not the revised explanation.
        Remember that explanation can contain multiple same errors."""

        input_for_err_type = "Claim: " + df["claim"][idx] +"\n" + "label: " + df["label"][idx] + "\n" + "Source: " + df["evidence"][idx] + "\n" + "Generated Explanation: " + df["explanation_1"][idx] + "\n \n" + quest_err_type
        input_for_type_err = "Claim: " + df["claim"][idx] +"\n" + "label: " + df["label"][idx] + "\n" + "Source: " + df["evidence"][idx] + "\n" + "Generated Explanation: " + df["explanation_1"][idx] + "\n \n" + quest_type_err

        expl_err_type = response_API(role_err_type, input_for_err_type)
        expl_type_err = response_API(role_type_err, input_for_type_err)

        log_err_type = [{"role": "user", "content": input_for_err_type}, {"role": "assistant", "content": expl_err_type},]
        log_type_err = [{"role": "user", "content": input_for_type_err}, {"role": "assistant", "content": expl_type_err},]

        quest_judge = "Please assess whether the feedback from both the first and second professional analyzers aligns. If their feedback matches, return only \"True\". If it does not, return only \"False\"."
        input_for_judge = "Feedback from the first professoinal analyzer: \"" + expl_err_type  + "\" \n" + "Feedback from the second professinal analzer: \" " + expl_type_err + "\" \n\n" + quest_judge
        label_from_judge = response_API_gpt_16k(role_judge, input_for_judge)

        return log_err_type, log_type_err, label_from_judge
        

    def debate(log_err_type, log_type_err):
        role_err_type = "You are a professional analyzer who find potential errors, which might weaken faithfulness, in the generated explanation (not in the source) and categorize them according to predefined error types. Thoroughly comprehend the provided source and the task carefully."
        role_type_err = "You are a professional analyzer who find errors, classified by predefined error types, in the generated explanation (not in the source) and provide feedback for correcting them. Thoroughly comprehend the provided source and the task carefully."
        role_judge = "You are a professional analyzer responsible for assessing whether the feedback from both the first and second professional analyzers aligns. If their feedback matches, return only \"True\". If it does not, return only \"False\"."
        role_extractor = "You are a professional copier who only extracts result on the last step of step by step instruction. You must give output without any extra word."

        quest = """Your task: 
        Step 1: Take your whole previous feedback. 
        Step 2: Compare your previous feedback with feedback from another professional analyzer to check whether your previous feedback contains any wrong error or feedback.
        Step 3: Find the errors or feedbacks that you think they are valid and should be added to your feedback from other's feedbacks (errors must be found from the generated explanation not the feedback). 
        Step 4: Rewrite the feedback based from your previous feedback using the answers from the steps above. Do not add any extra words than feedback. Remember you should follow this rule: do not to copy feedback from other and provide what are errors, exact senteces where the errors are found with quotation, and feedbacks.
    """

        input_err_type =  quest + "\"\n\n"  + "These are feedbacks from another professional analyzer: \"" + log_type_err[-1]["content"]
        input_type_err = quest + "\"\n\n" + "These are feedbacks from another professional analyzer: \"" + log_err_type[-1]["content"]
        

        log_err_type.append({"role" : "user", "content" : input_err_type})
        log_type_err.append({"role" : "user", "content" : input_type_err})

        output_err_type = response_API_continue(role_err_type, log_err_type)
        output_type_err = response_API_continue(role_type_err, log_type_err)

        log_err_type.pop()
        log_type_err.pop()

        log_err_type.pop()
        log_type_err.pop()

        log_err_type.append({"role": "assistant", "content": output_err_type})
        log_type_err.append({"role": "assistant", "content": output_type_err})

        quest_judge = "Please assess whether the feedback from both the first and second professional analyzers are akin. If their feedback matches, return only \"True\". If it does not, return only \"False\"."
        input_for_judge = "Feedback from the first professoinal analyzer: \"" + output_err_type  + "\" \n" + "Feedback from the second professinal analzer: \" " + output_type_err + "\" \n\n" + quest_judge
        label_from_judge = response_API_gpt_16k(role_judge, input_for_judge)


        return log_err_type, log_type_err, label_from_judge

    def finalize(log_err_type, log_type_err):
        role_final = "You are a professional writer who finalizes the two akin feedbacks into one."
        quest_final = "Please finalizes the given two akin feedbacks into one. Rememebr you must not modify any information and must provide what are errors, exact senteces where the errors are found with quotation, and feedbacks. "
        input_final = "Feedback 1: \n \" " + log_err_type[-1]["content"] + "\"\n\n" + "Feedback 2: \n \" " +  log_type_err[-1]["content"] + "\"\n\n" + quest_final
        pl = response_API_gpt_16k(role_final, input_final)
        return pl


    def one_time_debation(idx):
        log_err_type, log_type_err, label = init_debate(idx)
        output = [log_err_type[-1]["content"], log_type_err[-1]["content"],]

        for i in range(10):
            print(label[:4])
            
            if label[:4] != "True" and label[:4] != "true" and label[:4] != "TRUE":
                log_err_type, log_type_err, label = debate(log_err_type, log_type_err)
            else:
                break

        role_final = "You are a professional writer who returns the final ouput which comprehend all feedbacks."
        quest_final = "Please return the final output which comprehend given two feedbacks. Rememebr you must not modify any information and must provide what are errors, exact senteces where the errors are found with quotation, and feedbacks. "
        input_final = "Feedback 1: \n \" " + log_err_type[-1]["content"] + "\"\n\n" + "Feedback 2: \n \" " +  log_type_err[-1]["content"] + "\"\n\n" + quest_final
        pl = response_API_gpt_16k(role_final, input_final)
        

        output.append(pl)
        return output


    def refinement(idx, feedback):
        role_refine = "You are a professional writer who revises the explanation as given feedback says without any modification other than feedback."
        quest_refine = "Please revise generated explanation for label on fact-checking using the given feedback without any modification other than feedback says."
        input_refine = "Claim: " + df["claim"][idx] +"\n\n" + "label: " + df["label"][idx] + "\n\n" + "Source: " + df["evidence_source"][idx] + "\n\n" + "Generated Explanation: " + df["explanation_1"][idx] + "\n \n" + "Feedback: \n\t\"" + feedback + "\"\n\n" + quest_refine

        output = response_API_gpt_16k(role_refine, input_refine)
        return output


    for k in range(len(df)):
        temp  = one_time_debation(k)
        final = refinement(k, temp[-1])
        df["MADR"][k] = final

    return df
