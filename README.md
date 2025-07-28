# Challenge 1B: Persona-Driven Document Intelligence

## Overview
This solution analyzes document collections and extracts the most relevant sections based on a specific persona and their job requirements. It provides intelligent content prioritization and detailed subsection analysis.

## System Architecture

### Input Processing
- Reads document collections (3-10 PDFs per collection)
- Processes persona definitions and job requirements from JSON configuration files
- Extracts text while preserving document structure and page information

### Intelligence Engine
- **Persona Recognition**: Identifies user type and applies appropriate analysis criteria
- **Relevance Scoring**: Multi-factor algorithm considering keyword matching, context, and content quality
- **Section Ranking**: Hierarchical importance assignment based on relevance to user needs
- **Subsection Analysis**: Detailed extraction of most pertinent content segments

### Output Generation
- Structured JSON output with metadata, ranked sections, and detailed subsection analysis
- Importance rankings and relevance scores for all extracted content

## Key Features

### Multi-Domain Support
- **Academic Research**: Optimized for literature reviews, methodologies, and findings
- **Business Analysis**: Focused on financial data, market trends, and strategic insights
- **Educational Content**: Emphasizes key concepts, definitions, and learning materials

### Persona Adaptability
- **Researchers**: Prioritizes methodology, results, and analytical content
- **Students**: Focuses on explanations, examples, and fundamental concepts
- **Analysts**: Emphasizes metrics, trends, and performance data
- **Managers**: Highlights strategy, implementation, and objective-oriented content

### Intelligent Content Extraction
- Context-aware section identification
- Relevance-based importance ranking
- Detailed subsection analysis with refined text extraction

## Technical Implementation

### Libraries Used
- **PyMuPDF**: Advanced PDF text extraction with formatting preservation
- **NumPy**: Efficient numerical computations for scoring algorithms
- **Scikit-learn**: Text analysis and similarity calculations
- **Re**: Pattern matching for section identification

### Performance Features
- CPU-optimized processing for amd64 architecture
- Memory-efficient streaming text analysis
- Offline operation with no network dependencies
- Processing time <60 seconds for document collections

## Input Format
```json
{
  "documents": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Prepare comprehensive literature review focusing on methodologies and benchmarks"
}
```

## Output Format
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Literature review preparation",
    "processing_timestamp": "2025-01-28T10:30:00"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 5,
      "section_title": "Methodology",
      "importance_rank": 1
    }
  ],
  "sub_section_analysis": [
    {
      "document": "doc1.pdf",
      "page_number": 5,
      "refined_text": "The proposed methodology utilizes...",
      "relevance_score": 95.2
    }
  ]
}
```

## Build and Run Instructions

### Building the Docker Image
```bash
docker build --platform linux/amd64 -t persona-doc-analyzer:v1 .
```

### Running the Solution
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none persona-doc-analyzer:v1
```

## Directory Structure
```
input/
├── Collection1/
│   ├── PDFs/
│   │   ├── document1.pdf
│   │   └── document2.pdf
│   └── challenge1b_input.json
└── Collection2/
    ├── PDFs/
    └── challenge1b_input.json
```

## Performance Characteristics
- Processing time: <60 seconds per document collection
- Model size: <1GB total footprint
- Memory usage: Optimized for 16GB RAM systems
- CPU-only execution on linux/amd64 architecture
- Offline operation with no network requirements

## Scoring Optimization
- **Section Relevance**: Advanced keyword matching and context analysis
- **Sub-Section Quality**: Detailed content extraction with relevance scoring
- **Multilingual Support**: Unicode-aware text processing for international documents