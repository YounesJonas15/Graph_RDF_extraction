import pytest
from py.gpt_coref_resolver import coreference_resolver


def test_coreference_resolver_basic():
    # Exemple de texte avec des co-références
    input_text = "John is a doctor. He works at a hospital."
    expected_output = "John is a doctor. John works at a hospital."

    # Appeler la fonction de résolution
    resolved_text = coreference_resolver(input_text)

    # Vérifier si la co-référence est bien résolue
    assert resolved_text == expected_output, "La résolution de co-référence a échoué."
