# PDF Parser – Structured JSON Extraction

## Objective
Build a Python program that parses a PDF file and extracts its content into a **structured JSON format**.  
The JSON preserves **page hierarchy**, **sections/subsections**, and identifies **paragraphs, tables, and charts**.

---

## Features
- Extracts text content as **paragraphs** with section and subsection information  
- Detects and extracts **tables** using `pdfplumber`  
- Optionally extracts **charts/images** from the PDF and saves them locally  
- Organizes extracted data by **page-level hierarchy**  
- Saves results as a **clean JSON file**  

---

## Installation

Clone this repository and install dependencies:

```bash
git clone https://github.com/your-username/pdf-parser.git
cd pdf-parser
pip install -r requirements.txt

---

## Running The Script

'''bash
python pdf_parser.py

