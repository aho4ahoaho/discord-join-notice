import openai
from os import getenv
from romantokana import englishkana
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = getenv("OPENAI_ORG_ID")
MODEL = "gpt-3.5-turbo"

if OPENAI_API_KEY is None or OPENAI_ORG_ID is None:
    print("OpenAI API key or Org ID not found")
    exit()
openai.organization = OPENAI_ORG_ID
openai.api_key = OPENAI_API_KEY


def getPhonetic(text: str):
    result = ""
    try:
        context = "次のゲーマーのユーザー名をひらがなにしてください。出力は読みだけです。\n{}".format(text)
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "user", "content": context}],
            max_tokens=60,
            temperature=0.0,
        )
        result = response.choices[0].message.content.strip()
    except:
        result = englishkana(text)
    return result
