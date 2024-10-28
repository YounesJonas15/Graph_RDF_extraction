"""
Ce module fournit la classe RDFGrapher pour créer et visualiser des graphes RDF
à partir de triplets d'entrée.
"""

from rdflib import Graph, Namespace, Literal
from IPython.display import display, Image
from rdflib.tools.rdf2dot import rdf2dot
from dateutil.parser import parse
import pydotplus
import tempfile
import os


class RDFGrapher:
    """
    Classe pour gérer la création et la visualisation de graphes RDF.
    """

    def __init__(self):
        """
        Initialise un nouvel objet RDFGrapher avec des espaces de noms prédéfinis
        et un graphe RDF vide.
        """
        self.EX = Namespace("http://example.org/")
        self.DB = Namespace("http://dbpedia.org/resource/")
        self.g = Graph()

    def __is_uri__(self, uri: str) -> bool:
        """
        Vérifie si l'entrée donnée est une URI.

        Args:
            uri (str): L'URI à vérifier.

        Returns:
            bool: True si l'entrée est une URI, sinon False.
        """
        return "http://" in uri

    def __is_literal__(self, element: str) -> bool:
        """
        Vérifie si l'élément donné est un littéral ou non.

        Args:
            element (str): L'élément à vérifier.

        Returns:
            bool: True si l'élément est un littéral, sinon False.
        """
        if self.is_date(element):
            # Si c'est une date valide, on le considère comme un littéral
            date_object = parse(element)
            date_without_time = date_object.strftime(
                "%Y-%m-%d"
            )  # Format ISO 8601 pour la date
            return True

        if "http://" in element:
            # Si c'est une URI, ce n'est pas un littéral
            return False

        return True

    def is_date(self, date_str: str) -> bool:
        """
        Vérifie si la chaîne donnée peut être interprétée comme une date.

        Args:
            date_str (str): La chaîne à vérifier.

        Returns:
            bool: True si c'est une date valide, sinon False.
        """
        try:
            parse(date_str)
            return True
        except ValueError:
            return False

    def __transform_to_rdflibURIs(self, triplet_list):
        """
        Transforme les triplets d'entrée en triplets RDF.

        Args:
            triplet_list (list): Liste de triplets à transformer.

        Returns:
            dict: Un dictionnaire associant les éléments aux URIs ou littéraux correspondants.
        """
        my_set = {
            element.replace(" ", "_").replace("'", "").strip()
            for tple in triplet_list
            for element in (tple[0], tple[2])
        }
        my_dict = {}
        for element in my_set:
            # Vérification si l'élément est une URI
            if self.__is_uri__(element):
                element_plitted = element.split("/")[
                    -1
                ]  # Extrait le dernier segment de l'URL
                if "http://dbpedia.org" in element:
                    my_dict[element] = self.DB[element_plitted]
                else:
                    my_dict[element] = self.EX[element_plitted]
            else:
                my_dict[element] = Literal(element)
        return my_dict

    def transform_triplets_to_rdflib(self, triplet_list):
        """
        Transforme les triplets d'entrée en objets RDFLib.

        Args:
            triplet_list (list): Liste de triplets à transformer.

        Returns:
            list: Liste de triplets modifiés au format RDFLib.
        """
        my_dict = self.__transform_to_rdflibURIs(triplet_list)
        modified_triplet_list = []
        for a_tuple in triplet_list:
            # Transformation des sujets et objets en RDFLib
            subject = my_dict[a_tuple[0].replace(" ", "_").replace("'", "").strip()]
            object_ = my_dict[a_tuple[2].replace(" ", "_").replace("'", "").strip()]

            # Extraction du dernier segment du prédicat et transformation en URIRef
            predicat = a_tuple[1]
            predicat_splitted = (
                predicat.split("/")[-1].replace(" ", "_").replace("'", "")
            )

            if "http://dbpedia.org" in predicat:
                predicat = self.DB[predicat_splitted]
            else:
                predicat = self.EX[predicat_splitted]

            modified_triplet_list.append((subject, predicat, object_))

        return modified_triplet_list

    def __add_all_triplets_to_graph(self, triplet_list):
        """
        Ajoute tous les triplets à l'objet graphe RDF.

        Args:
            triplet_list (list): Liste de triplets à ajouter au graphe.
        """
        for a_tuple in triplet_list:
            self.g.add(a_tuple)

    def get_final_graph(self, triplet_list):
        """
        Récupère le graphe final après ajout des triplets.

        Args:
            triplet_list (list): Liste de triplets à ajouter au graphe.

        Returns:
            Graph: L'objet Graph contenant tous les triplets.
        """
        self.__add_all_triplets_to_graph(triplet_list)
        return self.g

    @staticmethod
    def visualize(g: Graph, image_name: str):
        """
        Visualise le graphe RDF en générant une image PNG et en l'enregistrant dans un dossier spécifié.

        Args:
            g (Graph): L'objet Graph à visualiser.
            image_name (str): Le nom du fichier d'image à enregistrer (sans extension).
        """
        # Définir le chemin du dossier de sortie
        output_directory = "resultat_graph"

        # Créer le dossier s'il n'existe pas déjà
        os.makedirs(output_directory, exist_ok=True)

        # Chemin complet du fichier image
        output_file_path = os.path.join(output_directory, f"{image_name}.png")

        # Utilisation d'un fichier temporaire pour le graphe
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_dot:
            rdf2dot(g, temp_dot)
            temp_dot.flush()
            dg = pydotplus.graph_from_dot_file(temp_dot.name)

            # Enregistrer le graphe en image PNG dans le dossier spécifié
            dg.write_png(output_file_path)

        # Optionnel : afficher l'image dans l'environnement Jupyter (si nécessaire)
        display(Image(output_file_path))
