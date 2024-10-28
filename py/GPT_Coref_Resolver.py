"""
Ce module fournit une fonction pour résoudre les co-références dans un texte donné en utilisant 
un modèle de langage (GPT-4) via LangChain.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()


def coreference_resolver(text: str) -> str:
    """
    Résout les co-références dans le texte donné en utilisant un modèle de langage.

    Args:
        text (str): Le texte d'entrée dans lequel les co-références doivent être résolues.

    Raises:
        ValueError: Si le texte d'entrée est vide ou ne contient que des espaces.

    Returns:
        str: Le texte modifié avec les co-références résolues, ou None en cas d'erreur.
    """

    # Vérification que le texte n'est pas vide
    if not text.strip():
        raise ValueError("Le texte d'entrée ne peut pas être vide.")

    # Modèle de prompt pour la résolution des co-références
    summary_template = """
    Réécrivez le texte suivant en résolvant les co-références :
    
    Texte : {text}
    
    Remplacez chaque pronom ou expression référentielle dans le texte par l'entité clé correspondante 
    du dictionnaire pour assurer clarté et cohérence.
    """

    # Création du modèle de prompt à partir du template défini
    summary_prompt_template = PromptTemplate(
        input_variables=["text"], template=summary_template
    )

    # Initialisation du modèle de langage avec des paramètres spécifiques
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Création d'une chaîne combinant le prompt et le modèle
    chain = summary_prompt_template | llm

    try:
        # Invocation de la chaîne avec le texte fourni
        resolved_text = chain.invoke({"text": text})
        return resolved_text.content
    except Exception as e:
        # Gestion des erreurs en cas de problème lors de l'invocation
        print(f"Une erreur est survenue : {e}")
        return None
