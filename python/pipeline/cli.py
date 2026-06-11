"""CLI entry point for running the anime web crawler"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .step1_crawler import AnimeCrawler


def main():
    parser = argparse.ArgumentParser(description="Crawl anime websites")
    parser.add_argument("--series", required=True, help="Series name")
    parser.add_argument("--start-url", required=True, help="Starting URL for crawl")
    parser.add_argument("--max-pages", type=int, default=None, help="Optional maximum pages to crawl")
    parser.add_argument(
        "--output-format",
        choices=("txt", "raw"),
        default="txt",
        help="Saved page format: extracted text or raw HTML",
    )
    parser.add_argument("--output", type=str, default=None, help="Output file path (JSON)")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    async def run_crawl():
        crawler = AnimeCrawler()
        
        print(f"Starting crawl for '{args.series}' from {args.start_url}")
        if args.max_pages is not None:
            print(f"Max pages: {args.max_pages}\n")
        else:
            print("Max pages: unlimited\n")
        print(f"Output format: {args.output_format}\n")
        
        results = await crawler.crawl_series(
            start_url=args.start_url,
            series=args.series,
            max_pages=args.max_pages,
            output_format=args.output_format,
        )

        print("RESULTS:", len(results))

        for page in results[:5]:
            print(
                page.get("title"),
                len(page.get("content", ""))
            )

        Path("test.txt").write_text(
            "crawler executed",
            encoding="utf-8"
        )

        print("TEST FILE WRITTEN")
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\nResults saved to: {output_path}")
        else:
            # Print summary to console
            print(f"\n{'='*60}")
            print(f"Crawl Complete!")
            print(f"{'='*60}")
            print(f"Series: {args.series}")
            print(f"Pages Crawled: {len(results)}")
            
            if results:
                print(f"\nCrawled URLs:")
                for i, result in enumerate(results, 1):
                    title = result.get("title", "No Title")[:50]
                    url = result["url"]
                    print(f"  {i}. [{title}]")
                    print(f"     {url}")
        
        return results
    
    asyncio.run(run_crawl())


if __name__ == "__main__":
    main()
