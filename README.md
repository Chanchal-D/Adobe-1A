# Chanchal-1b

# Adobe India Hackathon 2025 - Round 1A Solution
## "Connecting the Dots Through Docs"

### 🎯 **Solution Overview**

This solution extracts document structure from PDFs by identifying titles and hierarchical headings (H1, H2, H3) with high accuracy. It uses advanced text consolidation and intelligent heading detection to handle various PDF formats without relying solely on font sizes.

### 🛠 **Technical Approach**

1. **Advanced Text Extraction**: Uses PyMuPDF with intelligent text consolidation to fix fragmentation issues
2. **Smart Heading Detection**: Multi-criteria approach combining:
   - Numbered section patterns (1., 1.1, 1.1.1)
   - Formatting analysis (size, bold, positioning)
   - Content analysis (avoiding sentences, bullet points)
   - Context awareness (relative to surrounding text)
3. **Hierarchical Classification**: Automatically determines H1/H2/H3 levels based on numbering depth and formatting hierarchy

### 📦 **Libraries Used**

- **PyMuPDF (fitz)**: PDF text extraction and document processing
- **Standard Python Libraries**: re, json, pathlib, statistics, collections
- **Total Model Size**: ~50MB (well under 200MB limit)
- **No ML Models**: Pure algorithmic approach for maximum speed and reliability

### 🚀 **Build and Run Instructions**

```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-intelligence:hackathon .

# Run the solution
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-intelligence:hackathon
```

### 📂 **Input/Output Format**

**Input**: Place PDF files in `/app/input/` directory

**Output**: JSON files in `/app/output/` with format:
```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "Background", "page": 2 },
    { "level": "H3", "text": "Historical Context", "page": 2 }
  ]
}
```

### ⚡ **Performance**

- **Speed**: <2 seconds for 50-page PDFs
- **Accuracy**: High precision heading detection across various PDF formats
- **Memory**: Efficient processing with minimal memory footprint
- **Offline**: No internet connection required

### 🧪 **Key Features**

- **Robust Text Consolidation**: Fixes fragmented text extraction
- **Multi-Format Support**: Handles academic papers, reports, forms, technical documents
- **Smart Filtering**: Avoids false positives (page numbers, dates, bullets)
- **Hierarchical Intelligence**: Accurate H1/H2/H3 level determination
- **Edge Case Handling**: Manages complex layouts and formatting variations

### 📁 **Project Structure**

```
├── Dockerfile
├── README.md
├── requirements.txt
├── src/
│   └── main.py
├── input/          # Place PDF files here
└── output/         # Generated JSON files
```

### 🔧 **Configuration**

The solution is pre-configured for optimal performance:
- Maximum 50 pages processed per PDF
- Intelligent heading detection thresholds
- Efficient memory management
- Error handling for malformed PDFs

### 🏆 **Adobe Hackathon Compliance**

✅ **Technical Requirements Met:**
- AMD64 CPU architecture support
- No internet access required (offline processing)
- Model size <200MB (algorithmic approach, no ML models)
- Execution time <10 seconds for 50-page PDFs
- Automatic processing from `/app/input` to `/app/output`
- Valid JSON output format as specified

✅ **Docker Requirements:**
- Working Dockerfile in root directory
- All dependencies installed within container
- Compatible with hackathon run commands

This solution is designed specifically for Adobe India Hackathon 2025 Round 1A requirements.