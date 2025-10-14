from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import spacy 
import logging

# Lazy load spaCy (lightweight)
nlp = spacy.load('en_core_web_sm')

# Lazy load model (global, load on first use)
model = None

def get_model():
    global model
    if model is None:
        logging.debug("Loading SentenceTransformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        logging.debug("Model loaded successfully")
    return model

logging.basicConfig(level=logging.DEBUG)
logging.debug("AI Comparator module loaded")

def preprocess_text(text):
    """
    Clean and prepare text using spaCy:
    - Tokenize, remove stopwords, lemmatize.
    - Extract key terms (nouns, verbs, adjectives).
    - Join back into a cleaned string for embedding.
    """
    if not text:
        return ""
    doc = nlp(text)
    
    tokens = [
        token.lemma_.lower() for token in doc
        if not token.is_stop and not token.is_punct and token.pos_ in ['NOUN', 'VERB', 'ADJ']
    ]
    return ' '.join(tokens)

def compute_equivalency(input_descs, dhofar_courses, is_set=False):
    if not dhofar_courses:
        return None, 0.0
    
    # Get model (lazy)
    m = get_model()
    
    # Preprocess Dhofar courses
    dhofar_descs = [preprocess_text(course.description or "") for course in dhofar_courses]
    
    # Preprocess input
    if is_set:
        processed_input_descs = [preprocess_text(desc) for desc in input_descs]
        combined_input = ' '.join(processed_input_descs)
        input_embedding = m.encode(combined_input)
    else:
        processed_input = preprocess_text(input_descs[0])
        input_embedding = m.encode(processed_input)
    
    # Encode Dhofar
    dhofar_embeddings = m.encode(dhofar_descs)
    
    # Similarities
    similarities = util.cos_sim(input_embedding, dhofar_embeddings)[0]
    max_idx = np.argmax(similarities)
    score = float(similarities[max_idx]) * 100
    
    return dhofar_courses[max_idx], score

def compute_plan_equivalency(input_plan, dhofar_plan):
    results = []
    for input_course in input_plan:
        matched, score = compute_equivalency([input_course['description']], dhofar_plan)
        results.append({'input': input_course, 'matched': matched, 'score': score})
    overall_score = np.mean([r['score'] for r in results])
    return results, overall_score