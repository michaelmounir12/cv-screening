"""
Skill keyword extraction using spaCy.
"""
import logging
from typing import List, Set
import re

logger = logging.getLogger(__name__)

# Common tech/soft skill patterns (spaCy en_core_web_sm may miss many)
SKILL_PATTERNS = [
    r'\b(python|java|javascript|typescript|c\+\+|c#|go|rust|ruby|php|swift|kotlin|scala)\b',
    r'\b(react|angular|vue|django|flask|fastapi|spring|node\.?js|express)\b',
    r'\b(aws|azure|gcp|docker|kubernetes|terraform|jenkins|ci/cd)\b',
    r'\b(sql|postgresql|mysql|mongodb|redis|elasticsearch)\b',
    r'\b(machine learning|ml|deep learning|nlp|computer vision|tensorflow|pytorch)\b',
    r'\b(agile|scrum|kanban|jira|git|github|gitlab)\b',
    r'\b(rest api|graphql|microservices|api development)\b',
    r'\b(leadership|project management|team lead|communication|problem solving)\b',
]

_skill_re = re.compile('|'.join(SKILL_PATTERNS), re.I)


class SkillExtractionService:
    """Extract skill keywords from resume text using spaCy + pattern matching."""
    
    _nlp = None
    
    @classmethod
    def _get_nlp(cls):
        if cls._nlp is None:
            try:
                import spacy
                cls._nlp = spacy.load("en_core_web_sm")
            except OSError:
                try:
                    import spacy
                    import subprocess
                    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                    cls._nlp = spacy.load("en_core_web_sm")
                except Exception as e:
                    logger.warning(f"spaCy model not available: {e}. Using pattern-only extraction.")
                    cls._nlp = False
        return cls._nlp
    
    @classmethod
    def extract_skills(cls, raw_text: str) -> List[str]:
        """
        Extract skill keywords from resume text.
        Combines spaCy NER (ORG, PRODUCT) with regex patterns.
        """
        if not raw_text or not raw_text.strip():
            return []
        
        skills: Set[str] = set()
        text_lower = raw_text.lower()
        
        # Pattern-based extraction
        for m in _skill_re.finditer(text_lower):
            s = m.group().strip().lower()
            if len(s) > 1:
                skills.add(s)
        
        # spaCy extraction (skills often appear as entities or noun chunks)
        nlp = cls._get_nlp()
        if nlp:
            try:
                doc = nlp(raw_text[:50000])
                for ent in doc.ents:
                    if ent.label_ in ("ORG", "PRODUCT", "GPE"):
                        val = ent.text.strip().lower()
                        if 2 <= len(val) <= 50 and val.replace(" ", "").isalnum():
                            skills.add(val)
                for chunk in doc.noun_chunks:
                    if chunk.root.dep_ in ("pobj", "dobj", "attr"):
                        val = chunk.text.strip().lower()
                        if 2 <= len(val) <= 40:
                            skills.add(val)
            except Exception as e:
                logger.warning(f"spaCy extraction failed: {e}")
        
        return sorted(skills)
