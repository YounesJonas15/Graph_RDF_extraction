from evaluation import compare_triplets_advanced, calcul_metrics


triplet_ref_manuel = [
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "is",
        "French public university",
    ),
    ("University of Versailles Saint-Quentin-en-Yvelines", "date of creation", "1991"),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "localisation",
        "department of Yvelines",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "localisation since 2002",
        "Hauts-de-Seine",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "constituent",
        "Paris-Saclay University.",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "Consiste",
        "eight separate campuses",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "localisation",
        "Versailles",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "localisation",
        "Saint-Quentin-en-Yvelines",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "localisation",
        "Mantes-en-Yvelines",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "localisation",
        "Vélizy-Villacoublay",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "localisation",
        "Rambouillet",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "part of",
        "Academy of Versailles",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "part of",
        "universités nouvelles",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "part of",
        "new universities",
    ),
    ("universités nouvelles", "inaugurated in", "Île-de-France region"),
    ("universités nouvelles", "inaugurated after the", "2000 University project"),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "population",
        "19,000 students",
    ),
    ("University of Versailles Saint-Quentin-en-Yvelines", "staff", "752 people"),
    ("University of Versailles Saint-Quentin-en-Yvelines", "teachers", "1,389"),
    ("University of Versailles Saint-Quentin-en-Yvelines", "researchers", "1,389"),
    ("University of Versailles Saint-Quentin-en-Yvelines", "external teachers", "285"),
    ("University of Versailles Saint-Quentin-en-Yvelines", "field", "natural science"),
    ("University of Versailles Saint-Quentin-en-Yvelines", "field", "social science"),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "field",
        "political science",
    ),
    ("University of Versailles Saint-Quentin-en-Yvelines", "field", "engineering"),
    ("University of Versailles Saint-Quentin-en-Yvelines", "field", "technology"),
    ("University of Versailles Saint-Quentin-en-Yvelines", "field", "medicine"),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "interdisciplinary courses",
        "economics",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "interdisciplinary courses",
        "ethics",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "interdisciplinary courses",
        "natural environment",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "interdisciplinary courses",
        "sustainable development",
    ),
    ("Versailles", "part of", "department of Yvelines"),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "Consiste",
        "eight separate campuses",
    ),
    ("Artificial intelligence", "focuses on", "Mark Zuckerberg"),
    ("machine learning", "enable AI systems to", "Mark Zuckerberg"),
    ("natural language processing", "enable AI systems to", "Mark Zuckerberg"),
    ("Facebook", "conceived by", "Mark Zuckerberg"),
]


triplet_rebel = [
    ("University of Versailles Saint-Quentin-en-Yvelines", "country", "French"),
    ("University of Versailles Saint-Quentin-en-Yvelines", "inception", "1991"),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "located in the administrative territorial entity",
        "Yvelines",
    ),
    ("French", "contains administrative territorial entity", "Hauts-de-Seine"),
    ("department", "country", "French"),
    ("Yvelines", "country", "French"),
    ("Yvelines", "instance of", "department"),
    ("Hauts-de-Seine", "country", "French"),
    ("Hauts-de-Seine", "instance of", "department"),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "parent organization",
        "Paris-Saclay University",
    ),
    (
        "Paris-Saclay University",
        "subsidiary",
        "University of Versailles Saint-Quentin-en-Yvelines",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "located in the administrative territorial entity",
        "Versailles",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "instance of",
        "universités nouvelles",
    ),
    (
        "University of Versailles Saint-Quentin-en-Yvelines",
        "located in the administrative territorial entity",
        "Saint-Quentin-en-Yvelines",
    ),
]

calcul_metrics(triplet_rebel, triplet_ref_manuel)
