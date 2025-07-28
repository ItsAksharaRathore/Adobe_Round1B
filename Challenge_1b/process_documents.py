import os
import json
import re
from pathlib import Path
import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime
from collections import Counter
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonaDocumentAnalyzer:
    def __init__(self):
        # Keywords for different personas and their typical focus areas
        self.persona_keywords = {
            'researcher': ['methodology', 'results', 'analysis', 'experiment', 'data', 'study', 'research', 'findings', 'hypothesis', 'literature'],
            'student': ['definition', 'example', 'concept', 'theory', 'principle', 'basics', 'fundamentals', 'explanation', 'overview', 'summary'],
            'analyst': ['trend', 'performance', 'metric', 'revenue', 'growth', 'market', 'financial', 'investment', 'risk', 'return'],
            'manager': ['strategy', 'implementation', 'team', 'project', 'planning', 'execution', 'leadership', 'management', 'objectives', 'goals'],
            'developer': ['code', 'implementation', 'algorithm', 'technical', 'system', 'architecture', 'framework', 'api', 'database', 'optimization'],
            'consultant': ['recommendation', 'solution', 'best practice', 'assessment', 'evaluation', 'improvement', 'process', 'efficiency', 'optimization'],
        }
        
        # Academic keywords for research contexts
        self.academic_keywords = ['abstract', 'introduction', 'methodology', 'results', 'discussion', 'conclusion', 'references', 'literature review']
        
        # Business keywords for business contexts
        self.business_keywords = ['executive summary', 'financial', 'revenue', 'profit', 'market', 'strategy', 'competitive', 'analysis']

    def extract_document_text(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with page and section information"""
        doc = fitz.open(pdf_path)
        document_data = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Split text into paragraphs/sections
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            for para_idx, paragraph in enumerate(paragraphs):
                if len(paragraph) > 50:  # Filter out very short paragraphs
                    document_data.append({
                        'document': Path(pdf_path).name,
                        'page': page_num + 1,
                        'section_id': f"p{page_num + 1}_{para_idx}",
                        'text': paragraph,
                        'word_count': len(paragraph.split())
                    })
        
        doc.close()
        return document_data

    def identify_sections(self, document_data: List[Dict]) -> List[Dict]:
        """Identify major sections in the document"""
        sections = []
        current_section = None
        
        for item in document_data:
            text = item['text']
            
            # Check if this looks like a section header
            if self.is_section_header(text):
                # If we have a current section, save it
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'document': item['document'],
                    'page': item['page'],
                    'section_title': text[:100] + "..." if len(text) > 100 else text,
                    'content': [item],
                    'importance_rank': 0
                }
            else:
                # Add to current section
                if current_section:
                    current_section['content'].append(item)
                else:
                    # Create a section for orphaned content
                    current_section = {
                        'document': item['document'],
                        'page': item['page'],
                        'section_title': f"Section starting at page {item['page']}",
                        'content': [item],
                        'importance_rank': 0
                    }
        
        # Don't forget the last section
        if current_section:
            sections.append(current_section)
        
        return sections

    def is_section_header(self, text: str) -> bool:
        """Determine if text is likely a section header"""
        text = text.strip()
        
        # Short text that might be a header
        if len(text) < 200 and len(text) > 5:
            # Check for header patterns
            header_patterns = [
                r'^\d+\.?\s+[A-Z]',  # Numbered sections
                r'^[A-Z\s]{5,50}$',  # All caps headers
                r'^(Abstract|Introduction|Methodology|Results|Discussion|Conclusion|References)',
                r'^(Chapter|Section|Part)\s+\d+',
                r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*$'  # Title case
            ]
            
            for pattern in header_patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    return True
        
        return False

    def calculate_relevance_score(self, text: str, persona: str, job_description: str) -> float:
        """Calculate relevance score based on persona and job requirements"""
        text_lower = text.lower()
        persona_lower = persona.lower()
        job_lower = job_description.lower()
        
        score = 0.0
        
        # 1. Direct keyword matching with job description
        job_words = set(re.findall(r'\b\w+\b', job_lower))
        text_words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Calculate keyword overlap
        common_words = job_words.intersection(text_words)
        if job_words:
            keyword_score = len(common_words) / len(job_words)
            score += keyword_score * 40  # 40% weight for direct keyword matching
        
        # 2. Persona-specific keyword matching
        persona_type = self.identify_persona_type(persona_lower)
        if persona_type in self.persona_keywords:
            persona_words = self.persona_keywords[persona_type]
            persona_matches = sum(1 for word in persona_words if word in text_lower)
            if persona_words:
                persona_score = persona_matches / len(persona_words)
                score += persona_score * 30  # 30% weight for persona relevance
        
        # 3. Academic vs Business context scoring
        if any(keyword in job_lower for keyword in ['research', 'study', 'academic', 'paper']):
            academic_matches = sum(1 for keyword in self.academic_keywords if keyword in text_lower)
            score += academic_matches * 5
        
        if any(keyword in job_lower for keyword in ['business', 'financial', 'market', 'revenue']):
            business_matches = sum(1 for keyword in self.business_keywords if keyword in text_lower)
            score += business_matches * 5
        
        # 4. Text length bonus (longer sections often contain more information)
        word_count = len(text.split())
        if word_count > 100:
            score += min(word_count / 100, 10)  # Max 10 points for length
        
        # 5. Section position bonus (earlier sections often more important)
        # This would be calculated at the section level
        
        return min(score, 100)  # Cap at 100

    def identify_persona_type(self, persona: str) -> str:
        """Identify the general type of persona"""
        persona_mappings = {
            'researcher': ['researcher', 'scientist', 'phd', 'academic'],
            'student': ['student', 'undergraduate', 'graduate', 'learner'],
            'analyst': ['analyst', 'investment', 'financial', 'business analyst'],
            'manager': ['manager', 'director', 'executive', 'leader'],
            'developer': ['developer', 'engineer', 'programmer', 'technical'],
            'consultant': ['consultant', 'advisor', 'specialist']
        }
        
        for persona_type, keywords in persona_mappings.items():
            if any(keyword in persona for keyword in keywords):
                return persona_type
        
        return 'general'

    def extract_subsections(self, section: Dict, persona: str, job_description: str) -> List[Dict]:
        """Extract and rank subsections from a major section"""
        subsections = []
        
        for item in section['content']:
            # Split long paragraphs into smaller subsections
            text = item['text']
            sentences = re.split(r'[.!?]+', text)
            
            # Group sentences into subsections (3-5 sentences each)
            subsection_size = 4
            for i in range(0, len(sentences), subsection_size):
                subsection_sentences = sentences[i:i+subsection_size]
                subsection_text = '. '.join(s.strip() for s in subsection_sentences if s.strip())
                
                if len(subsection_text) > 50:  # Filter very short subsections
                    relevance_score = self.calculate_relevance_score(subsection_text, persona, job_description)
                    
                    subsections.append({
                        'document': item['document'],
                        'page_number': item['page'],
                        'refined_text': subsection_text,
                        'relevance_score': relevance_score
                    })
        
        # Sort by relevance score
        subsections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return subsections[:10]  # Return top 10 subsections

    def rank_sections(self, sections: List[Dict], persona: str, job_description: str) -> List[Dict]:
        """Rank sections based on relevance to persona and job"""
        for section in sections:
            # Calculate section relevance score
            section_text = ' '.join([item['text'] for item in section['content']])
            section['relevance_score'] = self.calculate_relevance_score(section_text, persona, job_description)
        
        # Sort sections by relevance score
        sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Assign importance ranks
        for i, section in enumerate(sections):
            section['importance_rank'] = i + 1
        
        return sections

    def process_document_collection(self, input_file: str) -> Dict[str, Any]:
        """Process a collection of documents based on input configuration"""
        try:
            # Read input configuration
            with open(input_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            collection_path = Path(input_file).parent
            persona = config['persona']
            job_description = config['job_to_be_done']
            documents = config['documents']
            
            logger.info(f"Processing collection for persona: {persona}")
            logger.info(f"Job: {job_description}")
            
            # Extract text from all documents
            all_document_data = []
            for doc_name in documents:
                doc_path = collection_path / 'PDFs' / doc_name
                if doc_path.exists():
                    logger.info(f"Processing document: {doc_name}")
                    doc_data = self.extract_document_text(str(doc_path))
                    all_document_data.extend(doc_data)
                else:
                    logger.warning(f"Document not found: {doc_path}")
            
            # Identify sections across all documents
            all_sections = self.identify_sections(all_document_data)
            
            # Rank sections based on relevance
            ranked_sections = self.rank_sections(all_sections, persona, job_description)
            
            # Extract top sections for output
            top_sections = ranked_sections[:20]  # Top 20 sections
            
            extracted_sections = []
            sub_section_analysis = []
            
            for section in top_sections:
                extracted_sections.append({
                    'document': section['document'],
                    'page_number': section['page'],
                    'section_title': section['section_title'],
                    'importance_rank': section['importance_rank']
                })
                
                # Extract subsections from top 10 sections
                if section['importance_rank'] <= 10:
                    subsections = self.extract_subsections(section, persona, job_description)
                    sub_section_analysis.extend(subsections[:3])  # Top 3 subsections per section
            
            # Create output
            output = {
                'metadata': {
                    'input_documents': documents,
                    'persona': persona,
                    'job_to_be_done': job_description,
                    'processing_timestamp': datetime.now().isoformat()
                },
                'extracted_sections': extracted_sections,
                'sub_section_analysis': sub_section_analysis
            }
            
            return output
            
        except Exception as e:
            logger.error(f"Error processing document collection: {str(e)}")
            return {
                'metadata': {
                    'input_documents': [],
                    'persona': '',
                    'job_to_be_done': '',
                    'processing_timestamp': datetime.now().isoformat(),
                    'error': str(e)
                },
                'extracted_sections': [],
                'sub_section_analysis': []
            }

def process_collections():
    """Main function to process all document collections"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    analyzer = PersonaDocumentAnalyzer()
    
    # Look for input configuration files
    input_files = list(input_dir.glob("**/challenge1b_input.json"))
    
    if not input_files:
        logger.warning("No input configuration files found")
        return
    
    for input_file in input_files:
        try:
            logger.info(f"Processing collection: {input_file}")
            
            # Process the document collection
            result = analyzer.process_document_collection(str(input_file))
            
            # Generate output filename
            collection_name = input_file.parent.name
            output_filename = f"{collection_name}_output.json"
            output_path = output_dir / output_filename
            
            # Save JSON output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Generated {output_filename}")
            
        except Exception as e:
            logger.error(f"Failed to process collection {input_file}: {str(e)}")

if __name__ == "__main__":
    process_collections()