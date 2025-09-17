import os
import sys
import json
import re
from typing import List, Dict, Any, Optional, Tuple
import pdfplumber


class PDFParser:
    def __init__(self, extract_images=False, image_outdir='extracted_images'):
        self.extract_images = extract_images
        self.image_outdir = image_outdir
        self.current_section = None
        self.current_sub_section = None
        print(f"Parser initialized - Extract images: {extract_images}")

        if extract_images and not os.path.exists(image_outdir):
            os.makedirs(image_outdir, exist_ok=True)

    def is_financial_table(self, text: str) -> bool:
        keywords = ['net asset', 'return', 'risk', 'volatility', 'yield', 'performance']
        if any(k in text.lower() for k in keywords):
            return True
        if re.search(r'\d+(\.\d+)?%?', text):
            return True
        return False

    def is_chart_indicator(self, text: str) -> bool:
        chart_keywords = ['chart', 'figure', 'graph', 'as of', 'performance since']
        return any(k in text.lower() for k in chart_keywords)

    def extract_section_info(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        if not text:
            return None, None

        words = text.strip().split()
        if len(words) <= 10 and text.isupper():
            return text.strip(), None

        if text.endswith(':') and len(words) <= 8:
            return None, text.strip()

        return None, None

    def extract_images_from_page(self, page, page_num: int) -> List[str]:
        saved_images = []

        if hasattr(page, "images"):
            pil_img = page.to_image().original 
            for idx, img in enumerate(page.images):
                try:
                    bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                    cropped = pil_img.crop(bbox)
                    outpath = os.path.join(
                        self.image_outdir, f"page{page_num}_img{idx}.png"
                    )
                    cropped.save(outpath)
                    saved_images.append(outpath)
                except Exception as e:
                    print(f"Error extracting image {idx} from page {page_num}: {e}")

        return saved_images

    def parse_pdf(self, pdf_path: str, output_json: str) -> Dict[str, Any]:
        print(f"Opening PDF: {pdf_path}")
        data: Dict[str, Any] = {"pages": []}

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    print(f"Processing page {i}/{len(pdf.pages)}...")
                    page_data: Dict[str, Any] = {"number": i, "content": []}

                    # I am doing this for Extracting text blocks
                    try:
                        extracted_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                    except Exception as e:
                        print(f"Error extracting text from page {i}: {e}")
                        extracted_text = None

                    if extracted_text:
                        for line in extracted_text.split("\n"):
                            section, subsection = self.extract_section_info(line)
                            if section:
                                self.current_section = section
                            if subsection:
                                self.current_sub_section = subsection

                            # This is the block consisting of the json structure and data
                            block = {
                                "text": line,
                                "section": self.current_section,
                                "subsection": self.current_sub_section,
                                "is_financial_table": self.is_financial_table(line),
                                "is_chart": self.is_chart_indicator(line),
                            }
                            page_data["content"].append(block)

                    #I am doing this for Extracting tables
                    #If extraction is possible then
                    try:
                        tables = page.extract_tables()
                        for t_idx, table in enumerate(tables):
                            page_data["content"].append(
                                {
                                    "table_index": t_idx,
                                    "table_data": table,
                                    "section": self.current_section,
                                    "subsection": self.current_sub_section,
                                }
                            )
                    # If extraction is not possible then        
                    except Exception as e:
                        print(f"Error extracting tables from page {i}: {e}")

                    if self.extract_images:
                        images = self.extract_images_from_page(page, i)
                        if images:
                            page_data["images"] = images

                    data["pages"].append(page_data)

            # Saving output as json file
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return data

        except Exception as e:
            print(f"Fatal error parsing PDF: {e}")
            return {}


def main():
    print("--------------------")
    print("PDF Parser")
    print("--------------------")

    pdf_filename = input("Enter path to your PDF file: ").strip()
    if not os.path.exists(pdf_filename):
        print("File not found. Exiting.")
        return

    print(f"Uploaded file: {pdf_filename}")
    print(f"Processing PDF '{pdf_filename}'...")

    output_filename = "factsheet_output.json"

    #This is a parser instance
    pdf_parser = PDFParser(extract_images=True)
    result = pdf_parser.parse_pdf(pdf_filename, output_filename)

    if result:
        total_pages = len(result["pages"])
        total_content = sum(len(page["content"]) for page in result["pages"])

        print(f"\nProcessing complete!")
        print(f"Pages processed: {total_pages}")
        print(f"Total content blocks: {total_content}")
        print(f"\nResults saved to: {output_filename}")
    else:
        print("Processing failed.")


if __name__ == "__main__":
    main()
