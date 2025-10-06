from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import spacy 

nlp = spacy.load('en_core_web_sm')

# Load SentenceTransformer model (BERT-based for similarity)
model = SentenceTransformer('all-MiniLM-L6-v2')

def preprocess_text(text):
    """
    Clean and prepare text using spaCy:
    - Tokenize, remove stopwords, lemmatize (reduce words to base form).
    - Extract key terms (nouns, verbs, adjectives for focus on content).
    - Join back into a cleaned string for embedding.
    """
    if not text:
        return ""
    doc = nlp(text)
    # Filter: lemmas of non-stopwords, key POS tags (NOUN, VERB, ADJ)
    tokens = [
        token.lemma_.lower() for token in doc
        if not token.is_stop and not token.is_punct and token.pos_ in ['NOUN', 'VERB', 'ADJ']
    ]
    return ' '.join(tokens)

def compute_equivalency(input_descs, dhofar_courses, is_set=False):
    if not dhofar_courses:
        return None, 0.0
    
    # Preprocess Dhofar courses with spaCy
    dhofar_descs = [preprocess_text(course.description or "") for course in dhofar_courses]
    
    # Preprocess input
    if is_set:
        # Combine set descriptions after preprocessing
        processed_input_descs = [preprocess_text(desc) for desc in input_descs]
        combined_input = ' '.join(processed_input_descs)
        input_embedding = model.encode(combined_input)
    else:
        # For single or plan (per course)
        processed_input = preprocess_text(input_descs[0])
        input_embedding = model.encode(processed_input)
    
    # Encode preprocessed Dhofar descriptions
    dhofar_embeddings = model.encode(dhofar_descs)
    
    # Compute similarities
    similarities = util.cos_sim(input_embedding, dhofar_embeddings)[0]
    max_idx = np.argmax(similarities)
    score = float(similarities[max_idx]) * 100
    
    return dhofar_courses[max_idx], score

def compute_plan_equivalency(input_plan, dhofar_plan):
    results = []
    for input_course in input_plan:
        # Preprocess and compute for each input course
        matched, score = compute_equivalency([input_course['description']], dhofar_plan)
        results.append({'input': input_course, 'matched': matched, 'score': score})
    overall_score = np.mean([r['score'] for r in results])
    return results, overall_score