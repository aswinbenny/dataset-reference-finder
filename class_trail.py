import os
import re
import glob
import pandas as pd
from collections import defaultdict
import ftfy
import unicodedata
import fitz
from lxml import etree
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

class DatasetReferenceExtractor:
    """
    Class to extract dataset references and their contexts from XML and PDF files.
    Produces a final DataFrame with: row_id, article_id, dataset_id, context.
    """

    def __init__(self, regex_patterns: dict, context_window: int = 40):
        """
        Initialize the extractor with dataset ID regex patterns and context size.
        """
        self.regex_patterns = regex_patterns  # e.g., {'SAMN': r'\bSAMN\d+\b'}
        self.context_window = context_window  # in words
        self.master_results = []  # collect all processed rows here

    def clean_text(self, text):
        """
        Apply all cleaning rules to raw text (PDF or XML).
        """
        # 1. Fix encoding issues like mojibake or smart quotes
        text = ftfy.fix_text(text)

        # 2. Normalize ligatures and full-width characters
        text = unicodedata.normalize("NFKC", text)

        # 3. Remove non-printable control characters (ASCII 0–31 and 127)
        text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)

        # 4. Remove unnecessary backslashes before quotes (like d\'Océanographie → d'Océanographie)
        text = re.sub(r'\\([\'"“”‘’`´])', r'\1', text)

        # 5. Add space between glued lowercase-uppercase boundaries (e.g., datasetEuropean → dataset European)
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

        # 6. Insert space before URLs (e.g., doihttps://... → doi https://...)
        text = re.sub(r'(?<=[a-zA-Z])(?=https?://)', ' ', text)

        # 7. Replace all weird dash characters with standard hyphen
        text = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2212]', '-', text)

        # 8. Add space after punctuation if not followed by space
        text = re.sub(r'([,;!?)\]\}])(?=\S)', r'\1 ', text)

        # 9.Remove all symbols **except** alphanumeric, hyphen, underscore, dot, and space
        text = re.sub(r'[^\w\s\:\.\-_\/]', ' ', text)

        # 10.Collapse repeated valid symbols, while preserving `//`
        text = re.sub(r'-{2,}', '-', text)
        text = re.sub(r'_{2,}', '_', text)
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'/{3,}', '//', text)  # Keep `//` but collapse longer

        # 11. Flatten all whitespace (spaces, tabs, newlines) into a single space
        text = re.sub(r'\s+', ' ', text)

        # 12. Remove any leftover leading/trailing space
        return text.strip()

    def extract_text_from_xml(self, xml_path):
        """
        Extract text content from an XML file.
        """
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(xml_path, parser)
        root = tree.getroot()
        text_parts = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_parts.append(elem.text.strip())
            if elem.tail and elem.tail.strip():
                text_parts.append(elem.tail.strip())
        
        text =  ' '.join(text_parts)
        return self.clean_text(text)
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract raw text from a PDF file.
        """
        doc = fitz.open(pdf_path)
        text = " "
        for page in doc:
            text += page.get_text()
        doc.close()
        return self.clean_text(text)
    
    def extract_context(self, text, pattern, window=30):
        """
        Extract context around regex matches from given text.

        Parameters:
        - text (str): Input document text.
        - pattern (str): Regex pattern to match.
        - window (int): Number of words before and after match to include in context.

        Returns:
        - List of dicts with 'match' and 'context' keys.
        """
        #pattern = sel
        matches = []

        # Tokenize the full text once
        tokens = text.split()

        # Map character index → token index
        char_to_token = {}
        index = 0
        for i, tok in enumerate(tokens):
            index = text.find(tok, index)
            for j in range(index, index + len(tok)):
                char_to_token[j] = i
            index += len(tok)

        # Find matches using re.finditer()
        for match in re.finditer(pattern, text):
            raw_match = match.group()
            cleaned_match = re.sub(r'[\s]', '', raw_match)  # Remove spaces inside ID

            start_char = match.start()

            if start_char in char_to_token:
                token_index = char_to_token[start_char]
                start = max(0, token_index - window)
                end = min(len(tokens), token_index + window + 1)
                context_window = tokens[start:end]

                matches.append({
                    'match': cleaned_match,
                    'context': ' '.join(context_window)
                })

        return matches
    
    def score_context(self, ctx: str) -> int:
        """
        Score the extracted context using keyword heuristics.
        Used to rank multiple mentions of the same dataset in a file.
        """
        ctx_lower = ctx.lower()
        score = 0

        usage_keywords = [
            'used', 'generated', 'collected', 'curated', 'analyzed', 'assembled', 'created',
            'constructed', 'compiled', 'built', 'gathered', 'obtained', 'employed', 'leveraged',
            'utilized', 'processed', 'performed on', 'applied to', 'mapped'
        ]

        access_keywords = [
            'downloaded', 'retrieved', 'accessed', 'available from', 'available at',
            'accessible', 'submitted to', 'hosted on', 'obtained from', 'released by',
            'found at', 'acquired', 'provided by', 'supplied by', 'linked from'
        ]

        citation_keywords = [
            'refer to', 'cited', 'listed', 'archived in', 'included in', 'mentioned',
            'reported in', 'registered in', 'source for', 'data from'
        ]

        for kw in usage_keywords:
            if kw in ctx_lower:
                score += 3
        for kw in access_keywords:
            if kw in ctx_lower:
                score += 2
        for kw in citation_keywords:
            if kw in ctx_lower:
                score += 1

        return score
    
    def deduplicate_matches(self, matches: list) -> list:
        """
        For each dataset_id in an article, retain only one match — the highest scored one.
        If scores are equal, prefer the earliest in the text.
        """
        raise NotImplementedError

    def merge_pdf_xml_matches(self, pdf_matches: list, xml_matches: list) -> list:
        """
        Combine matches from PDF and XML. If same dataset_id appears in both,
        decide which context to keep (e.g., prefer XML, or best score).
        """
        raise NotImplementedError

    # --- MASTER PIPELINE ---

    def process_article(self, article_id: str, pdf_path: str = None, xml_path: str = None) -> None:
        """
        Process one article: extract text from available sources, extract context,
        deduplicate, merge, and append to master results.

        Parameters:
        - article_id (str): Unique ID of the article (e.g., filename without extension)
        - pdf_path (str): Path to PDF file (if exists)
        - xml_path (str): Path to XML file (if exists)
        """

        pdf_matches, xml_matches = [], []

        # --- 1. Extract from PDF ---
        if pdf_path:
            try:
                clean_pdf_text = self.extract_text_from_pdf(pdf_path)
                pdf_matches = self.extract_context(clean_pdf_text, article_id, source="pdf")
                pdf_matches = self.deduplicate_matches(pdf_matches)
            except Exception as e:
                print(f"[PDF ERROR] Article {article_id}: {e}")

        # --- 2. Extract from XML ---
        if xml_path:
            try:
                clean_xml_text = self.extract_text_from_xml(xml_path)
                xml_matches = self.extract_context(clean_xml_text, article_id, source="xml")
                xml_matches = self.deduplicate_matches(xml_matches)
            except Exception as e:
                print(f"[XML ERROR] Article {article_id}: {e}")

        # --- 3. Merge PDF + XML matches ---
        merged_matches = self.merge_pdf_xml_matches(pdf_matches, xml_matches)

        # --- 4. Append to master results ---
        self.master_results.extend(merged_matches)

    
    def run_on_folder(self, pdf_folder: str, xml_folder: str) -> pd.DataFrame:
        """
        Run the dataset reference extraction pipeline on all files in given folders.
        
        Parameters:
        - pdf_folder (str): Path to the folder containing PDF files.
        - xml_folder (str): Path to the folder containing XML files.
        
        Returns:
        - pd.DataFrame with columns: row_id, article_id, dataset_id, context
        """

        # Get all files
        pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
        xml_files = glob.glob(os.path.join(xml_folder, "*.xml"))

        # Map: article_id → file path
        pdf_map = {os.path.splitext(os.path.basename(p))[0]: p for p in pdf_files}
        xml_map = {os.path.splitext(os.path.basename(x))[0]: x for x in xml_files}

        # Union of all article IDs
        all_article_ids = set(pdf_map.keys()) | set(xml_map.keys())

        # Loop through each article
        for article_id in sorted(all_article_ids):
            pdf_path = pdf_map.get(article_id)
            xml_path = xml_map.get(article_id)

            self.process_article(article_id, pdf_path=pdf_path, xml_path=xml_path)

        # Create final DataFrame
        df = pd.DataFrame(self.master_results)
        df.insert(0, 'row_id', range(len(df)))

        return df[['row_id', 'article_id', 'dataset_id', 'context']]

                
