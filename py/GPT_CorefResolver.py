from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os

load_dotenv()


def coreference_resolver(text: str):
    if not text.strip():
        raise ValueError("The input text cannot be empty.")

    summary_template = """
    Rewrite the following text by resolving the coreferences:
    
    Text: {text}
    
    Replace each pronoun or referring expression in the text with the corresponding key entity from the dictionary to ensure clarity and coherence.
    """

    summary_prompt_template = PromptTemplate(
        input_variables=["text"], template=summary_template
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chain = summary_prompt_template | llm

    try:
        resolved_text = chain.invoke({"text": text})
        return resolved_text.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
