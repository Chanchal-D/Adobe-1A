#!/usr/bin/env python3
"""
Adobe Hackathon Challenge 1A Solution
Robust PDF Structure Extractor
"""

import json
import os
import re
import logging
import fitz  # PyMuPDF
from pathlib import Path
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, page_index_base=1):
        self.input_dir = Path("/app/input")
        self.output_dir = Path("/app/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.page_index_base = page_index_base
        

    def process_all(self):
        """Process all PDFs in input directory"""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.info("No PDF files found in input directory")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing {pdf_file.name}")
                result = self.process_pdf(pdf_file)
                
                output_file = self.output_dir / f"{pdf_file.stem}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Generated output: {output_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
                self.create_error_output(pdf_file)

    def create_error_output(self, pdf_file):
        """Create minimal output on error"""
        output_file = self.output_dir / f"{pdf_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"title": "", "outline": []}, f, indent=2)

    def process_pdf(self, pdf_path: Path) -> dict:
        """Process single PDF file"""
        doc = fitz.open(pdf_path)
        title = self.extract_title(doc)
        headings = self.extract_headings(doc, title)
        doc.close()
        
        return {
            "title": title,
            "outline": headings
        }

    def extract_title(self, doc) -> str:
        """Extract title using geometric analysis of first page"""
        if len(doc) == 0:
            return ""
        
        page = doc[0]
        width, height = page.rect.width, page.rect.height
        
        # Define title region (top-center 60% width, 10-30% height)
        title_rect = fitz.Rect(width*0.2, height*0.1, width*0.8, height*0.3)
        text = page.get_text("text", clip=title_rect).strip()
        
        # Find the most prominent title candidate
        if not text:
            return ""
        
        # Split into lines and find the most significant one
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return ""
        
        # Prefer all-caps or title-case lines first
        title_candidates = sorted(
            lines,
            key=lambda x: (
                -len(x),  # Longer text
                x.isupper(),  # All caps
                sum(1 for c in x if c.isupper()) / max(1, len(x))  # Title case density
            ),
            reverse=True
        )
        
        return title_candidates[0]

    def extract_headings(self, doc, title: str) -> list[dict]:
        """Extract hierarchical headings with semantic filtering"""
        if len(doc) == 0:
            return []
        
        headings = []
        body_font_size = self.calculate_body_font_size(doc)
        title = title.lower()
        
        for page_num in range(min(len(doc), 50)):  # Limit to 50 pages
            page = doc[page_num]
            width, height = page.rect.width, page.rect.height
            
            # Define header/footer regions
            header_region = fitz.Rect(0, 0, width, height*0.15)
            footer_region = fitz.Rect(0, height*0.85, width, height)
            
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text or len(text) > 200:
                            continue
                        
                        bbox = fitz.Rect(span["bbox"])
                        
                        # Skip header/footer content
                        if bbox.intersects(header_region) or bbox.intersects(footer_region):
                            continue
                        
                        # Skip text that matches the title
                        if text.lower() == title:
                            continue
                        
                        # Heading detection heuristics
                        is_heading = self.is_heading_candidate(
                            span, 
                            body_font_size, 
                            height,
                            bbox
                        )
                        
                        if is_heading:
                            level = self.determine_heading_level(
                                span["size"], 
                                body_font_size,
                                text
                            )
                            
                            if level:
                                headings.append({
                                    "level": level,
                                    "text": text,
                                    "page": page_num + self.page_index_base
                                })
        
        return self.deduplicate_headings(headings)
    
    def is_heading_candidate(self, span, body_size, page_height, bbox) -> bool:
        """Determine if text span is a heading candidate"""
        font_size = span["size"]
        text = span["text"].strip()
        
        # Skip common non-heading patterns
        non_heading_patterns = [
            r'^page\s+\d+', r'^©', r'@', r'www\.', r'\.com$',
            r'\d{5}(-\d{4})?$', r'\d+\.\d+\.\d+', r'^\d{1,2}/\d{1,2}/\d{4}$',
            r'^\d{1,2}:\d{2}\s*[ap]m?$', r'^rsvp$', r'^tel:', r'^fax:',
            r'^email:', r'^http[s]?://', r'^version\s', r'^rev\s',
            r'^confidential$', r'^draft$', r'^-\s*$'
        ]
        
        if any(re.search(p, text.lower()) for p in non_heading_patterns):
            return False
        
        # Size-based criteria
        size_ratio = font_size / body_size
        if size_ratio >= 1.5:
            return True
        
        # Style-based criteria
        if "bold" in span["font"].lower() and size_ratio >= 1.2:
            return True
        
        # Position-based criteria (top of page)
        if bbox.y0 < page_height * 0.25:
            return True
        
        # Structural patterns (numbered headings, section headers)
        if re.match(r'^(#+|§|\d+[\.\)]|\w\.)\s*\w', text):
            return True
            
        # Heading-like text patterns
        heading_patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case
            r'^(introduction|background|summary|conclusion|references|appendix)\b',
            r'.+[:]$'  # Ends with colon
        ]
        
        if any(re.match(p, text) for p in heading_patterns):
            return True
        
        return False

    def determine_heading_level(self, font_size, body_size, text) -> str:
        """Determine heading level with semantic analysis"""
        size_ratio = font_size / body_size
        
        # Content-based prioritization
        content_keywords = {
            "H1": ["overview", "introduction", "executive summary", "abstract", 
                   "conclusion", "recommendations", "appendix"],
            "H2": ["background", "methodology", "results", "discussion", 
                   "implementation", "timeline", "milestones"],
            "H3": ["limitations", "future work", "case study", "example",
                   "figure", "table", "footnote"]
        }
        
        text_lower = text.lower()
        for level, keywords in content_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return level
        
        # Size-based classification
        if size_ratio > 2.0:
            return "H1"
        elif size_ratio > 1.7:
            return "H2"
        elif size_ratio > 1.4:
            return "H3"
        else:
            return "H4"

    def calculate_body_font_size(self, doc) -> float:
        """Calculate median body font size from first 10 pages"""
        font_sizes = []
        
        for page_num in range(min(len(doc), 10)):
            page = doc[page_num]
            words = page.get_text("words")
            if not words:
                continue
                
            # Filter out obvious headings and footers
            for word in words:
                y_pos = word[3]  # y0 coordinate
                if 0.2 < y_pos/page.rect.height < 0.8:  # Middle 60% of page
                    font_sizes.append(word[5])  # Font size
        
        if not font_sizes:
            return 11.0
        
        # Use median to be robust to outliers
        return sorted(font_sizes)[len(font_sizes) // 2]

    def deduplicate_headings(self, headings: list[dict]) -> list[dict]:
        """Remove duplicate headings"""
        seen = set()
        unique = []
        
        for h in headings:
            # Create stable key (page + normalized text)
            normalized_text = re.sub(r'\W+', '', h["text"].lower())
            key = (normalized_text, h["page"])
            
            if key not in seen:
                seen.add(key)
                unique.append(h)
                
        return unique

def main():
    """Main entry point"""
    processor = PDFProcessor(page_index_base=1)
    processor.process_all()

if __name__ == "__main__":
    main()