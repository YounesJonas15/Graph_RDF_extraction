from transformers import pipeline
import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON

class KnowledgeGraphExtractor:
    def __init__(self, model_name="Babelscape/rebel-large"):
        # Initialize the triplet extraction pipeline
        self.triplet_extractor = pipeline(
            "text2text-generation", model=model_name, tokenizer=model_name
        )

    def extract_triplet(self, text):
        # Generate the output using the model
        generated_output = self.triplet_extractor(
            text, return_tensors=True, return_text=False
        )
        # Decode the generated token IDs into text
        extracted_text = self.triplet_extractor.tokenizer.batch_decode(
            [generated_output[0]["generated_token_ids"]]
        )[0]
        # Parse the generated text to extract triplets
        return self._extract_triplets(extracted_text)

    def _extract_triplets(self, text):
        triplets = []
        relation, subject, object_ = "", "", ""
        text = text.strip()
        current = "x"

        for token in (
            text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split()
        ):
            if token == "<triplet>":
                current = "t"
                if relation != "":
                    triplets.append(
                        {
                            "head": subject.strip(),
                            "type": relation.strip(),
                            "tail": object_.strip(),
                        }
                    )
                    relation = ""
                subject = ""
            elif token == "<subj>":
                current = "s"
                if relation != "":
                    triplets.append(
                        {
                            "head": subject.strip(),
                            "type": relation.strip(),
                            "tail": object_.strip(),
                        }
                    )
                object_ = ""
            elif token == "<obj>":
                current = "o"
                relation = ""
            else:
                if current == "t":
                    subject += " " + token
                elif current == "s":
                    object_ += " " + token
                elif current == "o":
                    relation += " " + token

        # Append the last triplet if valid
        if subject != "" and relation != "" and object_ != "":
            triplets.append(
                {
                    "head": subject.strip(),
                    "type": relation.strip(),
                    "tail": object_.strip(),
                }
            )

        return triplets

    def compose_URI(self, candidate_entity):
        try:
            page = wikipedia.page(candidate_entity, auto_suggest=False)
            entity_data = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
            }
            uri = entity_data["url"].split("/")[-1]
            return "http://dbpedia.org/resource/" + uri
        except wikipedia.DisambiguationError as e:
            return candidate_entity
        except Exception as e:
            return candidate_entity

    def extract_URIs(self, triplet_list):
        my_set = {
            element for tple in triplet_list for element in (tple["head"], tple["tail"])
        }
        print(my_set)
        my_dict = {key: self.compose_URI(key) for key in my_set}
        return my_dict

    def transform_to_rdf_triplet(self, triplet_list):
        dictionnaire_uri = self.extract_URIs(triplet_list)
        sujets = {a_tuple["head"] for a_tuple in triplet_list}
        modified_triplets = []
        for a_tuple in triplet_list:
            temp = [
                a_tuple["head"],
                a_tuple["type"],
                a_tuple["tail"],
            ]  # Accès via les clés

            temp[0] = dictionnaire_uri.get(temp[0], temp[0])
            if "http://dbpedia.org/resource/" not in temp[0]:
                temp[0] = temp[0].replace(" ", "_").replace("-", "_").replace("'", "")
                temp[0] = "http://example.org/" + temp[0]

                temp[2] = dictionnaire_uri.get(temp[2], temp[2])
            if temp[2] in sujets and not temp[2].startswith("http"):
                temp[2] = temp[2].replace(" ", "_").replace("-", "_").replace("'", "")
                temp[2] = "http://example.org/" + temp[2]

            modified_triplets.append(tuple(temp))

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