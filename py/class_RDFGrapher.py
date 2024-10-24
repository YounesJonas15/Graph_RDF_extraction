from rdflib import Graph, Namespace, Literal
from IPython.display import display, Image
from rdflib.tools.rdf2dot import rdf2dot
from dateutil.parser import parse
import pydotplus
import tempfile


class RDFGrapher:
    def __init__(self):
        self.EX = Namespace("http://example.org/")
        self.DB = Namespace("http://dbpedia.org/resource/")
        self.g = Graph()

    def __is_uri__(self, uri: str) -> bool:
        """
        méthode qui verifie si l'entrée est une URI
        """
        if "http://" in uri:
            return True
        return False

    def __is_literal__(self, element: str) -> bool:
        """_summary_

        Args:
            element (str): _description_

        Returns:
            bool: _description_
        """

        if self.is_date(element):
            date_object = parse(element)
            date_without_time = date_object.strftime(
                "%Y-%m-%d"
            )  # Format ISO 8601 pour la date
            return True

        if "http://" in element:
            return False

        return True

    def is_date(self, date_str: str) -> bool:
        try:
            t = parse(date_str)
            return date_str
        except ValueError:
            return False

    def __transform_to_rdflibURIs(self, triplet_list):
        """
         transformer les triplet en entrée , en triplet rdf

        Args:
            triplet_list (_type_): _description_

        Returns:
            _type_: _description_
        """
        my_set = {
            element.replace(" ", "_").replace("'", "").strip()
            for tple in triplet_list
            for element in (tple[0], tple[2])
        }
        my_dict = {}
        for element in my_set:
            # element = element.replace(' ', '_').replace("'", "").strip() #
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
        my_dict = self.__transform_to_rdflibURIs(triplet_list)
        modified_triplet_list = []
        for a_tuple in triplet_list:
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
        for a_tuple in triplet_list:
            self.g.add(a_tuple)

    def get_final_graph(self, triplet_list):
        self.__add_all_triplets_to_graph(triplet_list)
        return self.g

    @staticmethod
    def visualize(g: Graph):
        # Utilisation d'un fichier temporaire pour le graphe
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_dot:
            rdf2dot(g, temp_dot)
            temp_dot.flush()
            dg = pydotplus.graph_from_dot_file(temp_dot.name)

            # Générer le contenu du graphe en image PNG
            image_bytes = dg.create_png()
            return image_bytes
