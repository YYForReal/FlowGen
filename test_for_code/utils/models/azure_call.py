import os
from openai import AzureOpenAI

gpt35_key = "bc709d6234e04a80ab2d744eb2434086"
gpt4_key = "3367dada076a42d292dbc6dcd48c74ba"
os.environ["AZURE_OPENAI_API_KEY"] = gpt35_key
api_type = "azure"
os.environ["OPENAI_API_TYPE"] = api_type
endpoint = "https://lechuang.openai.azure.com/"
os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
version = "2023-05-15"
os.environ["AZURE_OPENAI_API_VERSION"] = version
deployment = "lechuang-gpt-35-bak"

prompt = f"""
Hello!
"""
messages = [
    {"role": "user", "content": prompt},
]


def get_openai_response(messages):

    client = AzureOpenAI(
        # This is the default and can be omitted
        api_key=gpt35_key,
        api_version=version,
        azure_endpoint=endpoint,
        azure_deployment=deployment
    )

    client = AzureOpenAI(
        # This is the default and can be omitted
        api_key=gpt4_key,
        api_version=version,
        azure_endpoint="https://lechuang-gpt4.openai.azure.com/",
        azure_deployment="lechuang-gpt-4-turbo-bak"
    )

    response = client.chat.completions.create(
        model="",
        messages=messages,
    )

    prediction = response.choices[0].message.content
    if prediction != "" and prediction is not None:
        return prediction.strip()


def get_model():
    client = AzureOpenAI(
        # This is the default and can be omitted
        api_key=gpt35_key,
        api_version=version,
        azure_endpoint=endpoint,
        azure_deployment=deployment
    )
    return client


# print(get_openai_response(messages))
