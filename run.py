import argparse
import json
import os
from ingest.resume_ingest import parse_docx_to_profile

def main():
    parser = argparse.ArgumentParser(description="Job Hunter CLI")
    parser.add_argument('--resume-docx', type=str, help='Path to resume.docx')
    parser.add_argument('--top', type=int, default=15)
    parser.add_argument('--remote-only', type=bool, default=False)
    parser.add_argument('--locations', type=str, default='')
    # ... other args as needed
    args = parser.parse_args()

    if args.resume_docx:
        profile = parse_docx_to_profile(args.resume_docx)
        with open('master_resume.json', 'w') as f:
            json.dump(profile, f, indent=2)
        print('Resume profile written to master_resume.json')
        # Continue pipeline: board selector, fetch, dedupe, rank, tailor, export, track
        # ...existing pipeline code...
    else:
        # ...existing pipeline code...
        pass

if __name__ == "__main__":
    main()
