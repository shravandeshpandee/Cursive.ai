import requests
import yake
from transformers import pipeline
from serpapi import GoogleSearch
import streamlit as st

# Cache and load summarizer
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

# Cache and load sentiment analyzer
@st.cache_resource
def load_sentiment_analyzer():
    return pipeline("sentiment-analysis")

def summarize_text(text, summarizer):
    """Summarize the given text."""
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def analyze_sentiment(text, sentiment_analyzer):
    """Perform sentiment analysis on the text."""
    result = sentiment_analyzer(text)[0]
    return result['label'], result['score']

from keybert import KeyBERT

from keybert import KeyBERT

def extract_keywords_with_google_links(text, top_n=3):
    """
    Extract unique keywords (phrases) and generate exact phrase Google search links.
    Removes repeated and subphrase duplicates.
    """
    kw_model = KeyBERT()
    raw_keywords = kw_model.extract_keywords(
        text, 
        keyphrase_ngram_range=(1, 3), 
        stop_words='english', 
        top_n=top_n * 3  # Extract more initially to filter later
    )

    unique_keywords = []
    seen_phrases = []

    for kw, _ in raw_keywords:
        kw_lower = kw.lower()
        # Skip if it's a subphrase of an existing keyword
        if not any(kw_lower in existing or existing in kw_lower for existing in seen_phrases):
            seen_phrases.append(kw_lower)
            unique_keywords.append(kw)

        if len(unique_keywords) >= top_n:
            break

    keyword_links = {}
    for kw in unique_keywords:
        # Use exact phrase search on Google (with quotes)
        search_link = f"https://www.google.com/search?q=%22{kw.replace(' ', '+')}%22"
        keyword_links[kw] = search_link

    return keyword_links



