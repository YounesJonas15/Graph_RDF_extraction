import streamlit as st

# Importer les packages depuis py
from py.gpt_coref_resolver import coreference_resolver
from py.rdf_grapher import RDFGrapher
from py.knowledge_graph_extractor import KnowledgeGraphExtractor


def main_with_coref_resolution(kge, text: str, graph_name: str):
    # Résoudre les co-références dans le texte
    resolved_text = coreference_resolver(text)

    # Extraire les triplets
    triplets = kge.extract_triplet(resolved_text)
    rdf_triplets = kge.transform_to_rdf_triplet(triplets)
    enriched_triplets = kge.enrichir_graph(rdf_triplets)

    # Générer le graphe RDF
    generate_graph(enriched_triplets, graph_name)

    # Afficher les triplets enrichis dans l'application Streamlit
    st.write("**Triplets enrichis :**")
    for triplet in enriched_triplets:
        st.write(triplet)


def generate_graph(triplet, name):
    rdfgraphe = RDFGrapher()
    rdf_graph_triplet = rdfgraphe.transform_triplets_to_rdflib(triplet)
    final_graph = rdfgraphe.get_final_graph(rdf_graph_triplet)

    # Visualiser et enregistrer le graphe
    rdfgraphe.visualize(final_graph, name)


def main():
    st.title("Extraction et Visualisation de Triplets RDF")
    st.write("Entrez votre texte pour extraire les triplets RDF enrichis.")

    text_input = st.text_area("Texte à analyser", height=300)
    graph_name_input = st.text_input("Nom du fichier pour le graphe (sans extension)")

    kge = KnowledgeGraphExtractor()

    if st.button("Générer les Triplets RDF Enrichis"):
        if text_input and graph_name_input:
            main_with_coref_resolution(kge, text_input, graph_name_input)
        else:
            st.warning(
                "Veuillez entrer du texte et un nom de fichier avant de soumettre."
            )


if __name__ == "__main__":
    main()
