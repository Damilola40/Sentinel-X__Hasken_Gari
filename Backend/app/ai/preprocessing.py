"""
Module 1: Preprocessing & Text Normalization Layer
Cleans raw text reports, normalizes punctuation/whitespace, extracts entity hints.
"""

import re
from typing import Dict, Any

class TextPreprocessor:
    def __init__(self):
        # Local Hausa & Nigerian phrasing normalizations
        self.replacements = {
            r"\b(lga|l\.g\.a)\b": "LGA",
            r"\b(fct)\b": "Federal Capital Territory",
            r"\b(yan\s*sakai|vigilante|vigilantes)\b": "community security group",
            r"\b(yan\s*bindiga|bandits|gunmen)\b": "armed actors",
        }

    def clean_text(self, text: str) -> str:
        """
        Cleans and standardizes raw incident text.
        """
        if not text:
            return ""
        
        cleaned = str(text).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        
        for pattern, replacement in self.replacements.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
            
        return cleaned

    def process_report(self, title: str, description: str) -> Dict[str, Any]:
        """
        Combines and cleans title + description into a unified report string.
        """
        clean_title = self.clean_text(title)
        clean_desc = self.clean_text(description)
        combined = f"{clean_title}. {clean_desc}".strip(". ")
        
        return {
            "clean_title": clean_title,
            "clean_description": clean_desc,
            "combined_text": combined
        }
