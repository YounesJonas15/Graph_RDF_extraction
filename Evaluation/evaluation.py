from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")
# Charger un modèle plus puissant
# model = SentenceTransformer('all-MiniLM-L12-v2')


# Générer des embeddings pour chaque partie des triplets et les comparer
def compare_triplets_advanced(triplet_a, triplet_b):
    # Convertir les triplets en phrases pour une comparaison sémantique
    sentence_a = " ".join(triplet_a)
    sentence_b = " ".join(triplet_b)

    # Générer des embeddings
    embedding_a = model.encode(sentence_a)
    embedding_b = model.encode(sentence_b)

    # Calculer la similarité cosinus
    similarity = cosine_similarity([embedding_a], [embedding_b])[0][0]

    return similarity > 0.85  # Seuil de similarité ajustable


# Comparaison avancée
result_advanced = compare_triplets_advanced(
    ("William Henry Gates III", "date of birth", "October 28, 1955"),
    ("William Henry Gates III", "born", "28 octobre 1955"),
)

print(f"Les triplets sont-ils similaires (approche avancée) ? {result_advanced}")


def calcul_metrics(triplets_rebel, triplets_ref):
    triplets_rebel_modified = []

    for t in triplets_rebel:
        a = t[0]
        b = t[1]
        c = t[2]
        if not isinstance(a, str):
            a = a.text
        if not isinstance(b, str):
            b = b.text
        if not isinstance(c, str):
            c = c.text
        nv_tuple = tuple((a, b, c))
        triplets_rebel_modified.append(nv_tuple)
    nbre_total_referentiel = len(triplets_ref)
    nbre_total_rebel = len(triplets_rebel_modified)
    correct = 0
    for triplet_rebel in triplets_rebel_modified:
        for triplet_ref in triplets_ref:
            if compare_triplets_advanced(triplet_rebel, triplet_ref):
                print(f"{triplet_rebel} = {triplet_ref}")
                correct += 1
                break

    rappel = correct / nbre_total_referentiel
    precision = correct / nbre_total_rebel
    f1_score = 2 * rappel * precision / (rappel + precision)
    return {"precision": precision, "rappel": rappel, "f1-score": f1_score}


triplet_rebel = [
    ('University of Versailles Saint-Quentin-en-Yvelines', 'country', 'French'),
    ('University of Versailles Saint-Quentin-en-Yvelines', 'inception', '1991'),
    ('University of Versailles Saint-Quentin-en-Yvelines', 'located in the administrative territorial entity', 'Yvelines'),
    ('French', 'contains administrative territorial entity', 'Hauts-de-Seine'),
    ('department', 'country', 'French'),
    ('Yvelines', 'country', 'French'),
    ('Yvelines', 'instance of', 'department'),
    ('Hauts-de-Seine', 'country', 'French'),
    ('Hauts-de-Seine', 'instance of', 'department'),
    ('University of Versailles Saint-Quentin-en-Yvelines', 'parent organization', 'Paris-Saclay University'),
    ('Paris-Saclay University', 'subsidiary', 'University of Versailles Saint-Quentin-en-Yvelines'),
    ('University of Versailles Saint-Quentin-en-Yvelines', 'located in the administrative territorial entity', 'Versailles'),
    ('University of Versailles Saint-Quentin-en-Yvelines', 'instance of', 'universités nouvelles'),
    ('University of Versailles Saint-Quentin-en-Yvelines', 'located in the administrative territorial entity', 'Saint-Quentin-en-Yvelines')
]