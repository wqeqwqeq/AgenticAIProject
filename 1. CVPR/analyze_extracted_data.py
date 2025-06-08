#!/usr/bin/env python3

import json
import argparse
from collections import Counter

def analyze_extracted_data(json_file: str) -> None:
    """
    Analyze the extracted CVPR paper data and provide statistics.
    
    Args:
        json_file (str): Path to the JSON file
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        print(f"📊 CVPR 2024 Papers Analysis")
        print(f"=" * 50)
        print(f"Total papers extracted: {len(papers)}")
        print()
        
        # Analyze document availability
        pdf_count = sum(1 for paper in papers if paper['doc_list']['pdf'])
        supp_count = sum(1 for paper in papers if paper['doc_list']['supp'])
        arxiv_count = sum(1 for paper in papers if paper['doc_list']['arxiv'])
        bibtex_count = sum(1 for paper in papers if paper['doc_list']['bibtex'])
        
        print(f"📄 Document Availability:")
        print(f"  PDF links: {pdf_count} ({pdf_count/len(papers)*100:.1f}%)")
        print(f"  Supplemental: {supp_count} ({supp_count/len(papers)*100:.1f}%)")
        print(f"  ArXiv links: {arxiv_count} ({arxiv_count/len(papers)*100:.1f}%)")
        print(f"  BibTeX entries: {bibtex_count} ({bibtex_count/len(papers)*100:.1f}%)")
        print()
        
        # Author statistics
        all_authors = []
        for paper in papers:
            all_authors.extend(paper['author_list'])
        
        unique_authors = set(all_authors)
        author_counts = Counter(all_authors)
        top_authors = author_counts.most_common(10)
        
        print(f"👥 Author Statistics:")
        print(f"  Total unique authors: {len(unique_authors)}")
        print(f"  Average authors per paper: {len(all_authors)/len(papers):.1f}")
        print(f"  Top 10 most prolific authors:")
        for i, (author, count) in enumerate(top_authors, 1):
            print(f"    {i:2d}. {author} ({count} papers)")
        print()
        
        # Title length statistics
        title_lengths = [len(paper['title']) for paper in papers]
        avg_title_length = sum(title_lengths) / len(title_lengths)
        
        print(f"📝 Title Statistics:")
        print(f"  Average title length: {avg_title_length:.1f} characters")
        print(f"  Shortest title: {min(title_lengths)} characters")
        print(f"  Longest title: {max(title_lengths)} characters")
        print()
        
        # Sample some papers
        print(f"📋 Sample Papers:")
        for i, paper in enumerate(papers[:3], 1):
            print(f"  {i}. {paper['title']}")
            print(f"     Authors: {', '.join(paper['author_list'][:3])}{'...' if len(paper['author_list']) > 3 else ''}")
            print(f"     PDF: {'✓' if paper['doc_list']['pdf'] else '✗'}")
            print(f"     ArXiv: {'✓' if paper['doc_list']['arxiv'] else '✗'}")
            print()
        
    except Exception as e:
        print(f"Error analyzing data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Analyze extracted CVPR 2024 paper data')
    parser.add_argument('--input', '-i',
                       default='cvpr2024_papers.json',
                       help='Input JSON file (default: cvpr2024_papers.json)')
    
    args = parser.parse_args()
    
    analyze_extracted_data(args.input)

if __name__ == '__main__':
    main() 