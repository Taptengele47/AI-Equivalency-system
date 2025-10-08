from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import spacy

nlp = spacy.load('en_core_web_sm')

model = None  # Lazy: Load only when needed

def load_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Or smaller 'all-MiniLM-L6-v2' for low RAM
    return model

def preprocess_text(text):
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
    
    m = load_model()  # Lazy load here (first use only)
    
    dhofar_descs = [preprocess_text(course.description or "") for course in dhofar_courses]
    
    if is_set:
        processed_input_descs = [preprocess_text(desc) for desc in input_descs]
        combined_input = ' '.join(processed_input_descs)
        input_embedding = m.encode(combined_input)
    else:
        processed_input = preprocess_text(input_descs[0])
        input_embedding = m.encode(processed_input)
    
    dhofar_embeddings = m.encode(dhofar_descs)
    similarities = util.cos_sim(input_embedding, dhofar_embeddings)[0]
    max_idx = np.argmax(similarities)
    score = float(similarities[max_idx]) * 100
    
    return dhofar_courses[max_idx], score

def compute_plan_equivalency(input_plan, dhofar_plan):
    m = load_model()  # Lazy for plans too
    results = []
    for input_course in input_plan:
        matched, score = compute_equivalency([input_course['description']], dhofar_plan)
        results.append({'input': input_course, 'matched': matched, 'score': score})
    overall_score = np.mean([r['score'] for r in results])
    return results, overall_score