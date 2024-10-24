"""
This module provides the KnowledgeGraphExtractor class for extracting knowledge graphs 
using Spacy and SPARQL.
"""
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy
import wikipedia
import modules.spacy_component


class KnowledgeGraphExtractor:
    """ 
    Classe permettant d'extraire et d'enrichir des triplets RDF à partir de texte en utilisant
    le modèle REBEL et des requêtes SPARQL sur DBpedia pour enrichir le graph.

    """
    def __init__(self, cpu_or_gpu=-1):
        if cpu_or_gpu not in [-1, 0]:
            raise ValueError("-1 or 0, we dont accept another value")
        self.nlp = spacy.load("en_core_web_sm")

        self.nlp.add_pipe(
            "rebel",
            after="senter",
            config={
                "device": cpu_or_gpu,  # Number of the GPU, -1 if want to use CPU
                "model_name": "Babelscape/rebel-large",
            },  # Model used, will default to 'Babelscape/rebel-large' if not given
        )

    def extract_triplet(self, texte : str):
        """Extracts knowledge triplets from the given text using Spacy NLP pipeline.

        Args:
            texte (str): The input text from which to extract triplets.

        Returns:
            List : A list of extracted triplets in the form (head, relation, tail)
        """
        texte = texte.replace("\n", " ").strip()
        doc = self.nlp(texte)
        #doc_list = self.nlp.pipe(texte)
        triplet_list = [
            (rel_dict["head_span"], rel_dict["relation"], rel_dict["tail_span"])  #extract from the new attribut "rel"
            for value, rel_dict in doc._.rel.items()
        ]
        return triplet_list

    def compose_uri(self, candidate_entity):
        """ compose the uri for an entity based on what found in wikipedia (same url)

        Args:
            candidate_entity (_type_): the entity is hear or relation

        Returns:
            _type_: URI DBpedia générée pour l'entité, soit le nom de l'entité si la recherche échoue.
        """
        try:
            page = wikipedia.page(candidate_entity, auto_suggest=False)
            entity_data = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
            }
            uri = entity_data["url"].split("/")[-1]
            return "http://dbpedia.org/resource/" + uri
        except:
            return candidate_entity

    def extract_uri(self, triplet_list):
        """
            Extrait les URIs pour chaque entité dans une liste de triplets RDF.

            Args:
            triplet_list (List[Tuple]): Liste de triplets, chaque triplet est une structure (head, relation, tail)
                                    où `head` et `tail` sont des entités et `relation` est une relation.

            Returns:
            dict: Un dictionnaire où les clés sont les entités (head et tail des triplets) et les valeurs sont leurs URIs.
        """
        my_set = {
            element for tple in triplet_list for element in (tple[0].text, tple[2].text)
        }
        my_dict = {key: self.compose_uri(key) for key in my_set}
        return my_dict

    def transform_to_rdf_triplet(self, triplet_list):
        """transformer les triplet extrait par le model nlp en triplet RDF 

        Args:
            triplet_list (list): list des triplet (Head, relation, tail) 

        Returns:
            list: list de triplet RDF (avec les uri)
        """
        # Extraction des URIs pour chaque entité présente dans la liste de triplets
        dictionnaire_uri = self.extract_uri(triplet_list)

        # Récupération de l'ensemble des sujets uniques (texte brut) des triplets
        sujets = {a_tuple[0].text for a_tuple in triplet_list}
        
        # Initialisation d'une liste vide pour stocker les triplets modifiés en format RDF
        modified_triplets = []

        # Parcourir chaque triplet de la liste donnée
        for a_tuple in triplet_list:
            # Convertir le triplet en liste pour faciliter la modification
            temp = list(a_tuple)
            
            # Transformation du sujet (head) en URI
            temp[0] = dictionnaire_uri.get(temp[0].text, temp[0])  # Cherche l'URI du sujet dans le dictionnaire
            if "http://dbpedia.org/resource/" not in temp[0]:  # Si ce n'est pas une URI DBpedia
                # Remplacement des espaces et caractères spéciaux par des underscores
                temp[0] = temp[0].replace(" ", "_")
                temp[0] = temp[0].replace("-", "_")
                temp[0] = temp[0].replace("'", "")
                # Ajout du préfixe "http://example.org/" pour former un URI valide si ce n'est pas DBpedia
                temp[0] = "http://example.org/" + temp[0]

            # Transformation de l'objet (tail) en URI
            temp[2] = dictionnaire_uri.get(temp[2].text, temp[2])  # Cherche l'URI de l'objet dans le dictionnaire
            # Si l'objet fait partie des sujets et n'est pas déjà une URI valide
            if temp[2] in sujets and not temp[2].startswith("http"):
                # Remplacement des espaces et caractères spéciaux par des underscores
                temp[2] = temp[2].replace(" ", "_")
                temp[2] = temp[2].replace("-", "_")
                temp[2] = temp[2].replace("'", "")
                # Ajout du préfixe "http://example.org/" pour former un URI valide
                temp[2] = "http://example.org/" + temp[2]

            # Ajout du triplet modifié à la liste finale des triplets RDF
            modified_triplets.append(tuple(temp))

        # Retourne la liste de triplets RDF modifiés
        return modified_triplets

    def check_is_dbpedia(self, resource):
        if "http://dbpedia.org/resource/" in resource:
            return True
        return False

    def get_predicate_sparql(self, a_tuple):
        uri_0 = a_tuple[0]
        old_predicate = a_tuple[1]
        uri_1 = a_tuple[2]
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery(
            f"""
      SELECT DISTINCT ?predicate
      WHERE {{
        <{uri_0}> ?predicate <{uri_1}> .
      }}
      """
        )
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            predicates = [
                result["predicate"]["value"]
                for result in results["results"]["bindings"]
            ]
            if not predicates:
                return [(uri_0, old_predicate, uri_1)]

            new_tuples = [(uri_0, value, uri_1) for value in predicates]
            new_tuples.append((uri_0, old_predicate, uri_1))
            return new_tuples
        except Exception as e:
            print(f"An error occurred: {e}")
            return [(uri_0, old_predicate, uri_1)]

    def get_resource_type(self, uri):
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery(
            f"""
        SELECT ?type
        WHERE {{
            <{uri}> rdf:type ?type .
            }}
        """
        )
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        types = [result["type"]["value"] for result in results["results"]["bindings"]]
        if not types:
            return None
        new_tuples = [
            (uri, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", value)
            for value in types[:10]
        ]
        return new_tuples

    def enrichir_graph(self, triplet_list):
        list_modified = []
        for a_tuple in triplet_list:
            if self.check_is_dbpedia(a_tuple[0]) and self.check_is_dbpedia(
                a_tuple[2]
            ):  # (uri0, pred, uri2)
                liste = self.get_predicate_sparql(a_tuple)
                list_modified.extend(liste)
            if self.check_is_dbpedia(a_tuple[0]):
                uri_0_types = self.get_resource_type(a_tuple[0])
                if uri_0_types is not None:
                    list_modified.extend(uri_0_types)
            if self.check_is_dbpedia(a_tuple[2]):
                uri_2_types = self.get_resource_type(a_tuple[2])
                if uri_2_types is not None:
                    list_modified.extend(uri_2_types)

            else:
                list_modified.append(tuple(a_tuple))

        return list_modified
