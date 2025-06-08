#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import sys

def extract_papers_from_html(html_file: str, output_file: str = None) -> bool:
    """
    Extract paper information from CVPR HTML file and save as JSON.
    
    Args:
        html_file (str): Path to the HTML file
        output_file (str, optional): Output JSON file path
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the HTML file
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        papers = []
        
        # Find all paper title elements
        paper_titles = soup.find_all('dt', class_='ptitle')
        
        for title_element in paper_titles:
            paper_info = {
                "title": "",
                "title_url": "",
                "author_list": [],
                "doc_list": {
                    "pdf": "",
                    "supp": "",
                    "arxiv": "",
                    "bibtex": ""
                }
            }
            
            # Extract title and title URL
            title_link = title_element.find('a')
            if title_link:
                paper_info["title"] = title_link.get_text().strip()
                paper_info["title_url"] = "https://openaccess.thecvf.com" + title_link.get('href', '')
            
            # Find the next dd elements for authors and links
            next_elements = title_element.find_next_siblings(['dd'])
            
            for dd in next_elements:
                # Extract authors from forms
                author_forms = dd.find_all('form', class_='authsearch')
                if author_forms:
                    for form in author_forms:
                        author_input = form.find('input', {'name': 'query_author'})
                        if author_input:
                            author_name = author_input.get('value', '').strip()
                            if author_name and author_name not in paper_info["author_list"]:
                                paper_info["author_list"].append(author_name)
                
                # Extract document links
                links = dd.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text().strip().lower()
                    
                    if text == 'pdf' and '/papers/' in href:
                        paper_info["doc_list"]["pdf"] = "https://openaccess.thecvf.com" + href
                    elif text == 'supp' and '/supplemental/' in href:
                        paper_info["doc_list"]["supp"] = "https://openaccess.thecvf.com" + href
                    elif text == 'arxiv':
                        paper_info["doc_list"]["arxiv"] = href
                
                # Extract bibtex
                bibref_div = dd.find('div', class_='bibref')
                if bibref_div:
                    paper_info["doc_list"]["bibtex"] = bibref_div.get_text().strip()
                    break  # Found the complete paper info, move to next paper
            
            # Only add papers that have at least title and some authors
            if paper_info["title"] and paper_info["author_list"]:
                papers.append(paper_info)
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = "cvpr2024_papers.json"
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully extracted {len(papers)} papers to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error extracting papers: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Extract CVPR 2024 paper information to JSON')
    parser.add_argument('--input', '-i',
                       default='cvpr2024.html',
                       help='Input HTML file (default: cvpr2024.html)')
    parser.add_argument('--output', '-o',
                       help='Output JSON file (default: cvpr2024_papers.json)')
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    success = extract_papers_from_html(args.input, args.output)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 