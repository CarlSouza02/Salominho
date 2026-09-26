"""Fases planejadas de Gênesis e questões da fase de demonstração."""
LEVELS = [
    ("A Criação", "Gênesis 1:1-5"),
    ("O Jardim", "Gênesis 2"),
    ("A Queda", "Gênesis 3"),
    ("Caim e Abel", "Gênesis 4"),
    ("Noé", "Gênesis 6–9"),
    ("Babel", "Gênesis 11"),
    ("Abraão", "Gênesis 12"),
    ("Isaque", "Gênesis 21"),
    ("Jacó", "Gênesis 27"),
    ("José", "Gênesis 37"),
]

QUESTIONS = [
    {
        "prompt": "Segundo Gênesis 1:1, o que Deus criou no princípio?",
        "choices": ["O templo", "Os céus e a terra", "Uma cidade", "O mar somente"],
        "correct": 1,
        "reference": "Gênesis 1:1",
        "explanation": "O versículo inicial apresenta a criação dos céus e da terra.",
    },
    {
        "prompt": "Em qual livro começa a narrativa da criação?",
        "choices": ["Êxodo", "Salmos", "Gênesis", "Provérbios"],
        "correct": 2,
        "reference": "Gênesis 1:1",
        "explanation": "Gênesis é o primeiro livro da Bíblia nessa organização.",
    },
    {
        "prompt": "Qual referência descreve o início da criação?",
        "choices": ["Salmos 23:1", "Mateus 5:3", "João 11:35", "Gênesis 1:1"],
        "correct": 3,
        "reference": "Gênesis 1:1",
        "explanation": "Gênesis 1:1 abre o relato da criação.",
    },
]
