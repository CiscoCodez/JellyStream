#!/usr/bin/env python3
"""
Series Structure Analyzer
Analyzes series structure: seasons, episodes, and movie counts
Input: data/tmp_name_url.json
Output: data/tmp_season_episode_data.json
set limit with [--limit] [num] flag.
set batch processing with [-b] [num] flag.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin
from pathlib import Path
import config

class SeriesStructureAnalyzer:
    def __init__(self, limit: Optional[int] = None, batch_size: Optional[int] = None):
        self.limit = limit
        self.batch_size = batch_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.data_folder = Path(config.DATA_DIR)
        self.input_file = self.data_folder / "tmp_name_url.json"
        self.output_file = self.data_folder / "tmp_season_episode_data.json"

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return a soup object."""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            return BeautifulSoup(response.content, 'html.parser')
        except Exception:
            return None

    def find_labeled_list(self, soup: BeautifulSoup, label_text: str):
        """Find the first <ul> whose text starts with a specific label."""
        for ul in soup.find_all('ul'):
            text = ul.get_text(" ", strip=True)
            if text.startswith(label_text):
                return ul
        return None

    def normalize_series_url(self, url: str) -> str:
        """Ensure all series URLs use the /serie/stream/ pattern."""
        if '/serie/stream/' in url:
            return url.rstrip('/')
        if '/serie/' in url:
            return url.replace('/serie/', '/serie/stream/', 1).rstrip('/')
        return url.rstrip('/')
    
    def load_series_data(self) -> List[Dict]:
        """Load series URLs from input file"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('series', [])
        except Exception as e:
            print(f"❌ Error loading {self.input_file}: {e}")
            return []
    
    def load_existing_data(self) -> Dict:
        """Load existing analyzed data if file exists"""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"📂 Found existing data: {data.get('total_series', 0)} series")
                return data
            except Exception as e:
                print(f"⚠️  Error loading existing data: {e}")
        return None
    
    def get_existing_urls(self, existing_data: Dict) -> set:
        """Get set of existing URLs to avoid duplicates"""
        if not existing_data or 'series' not in existing_data:
            return set()
        
        existing_urls = {series['url'] for series in existing_data['series']}
        print(f"🔍 Found {len(existing_urls)} existing series")
        return existing_urls
    
    def save_batch_data(self, new_series: List[Dict], existing_data: Dict = None) -> Dict:
        """Save batch data by merging with existing data"""
        if existing_data:
            # Merge with existing data
            all_series = existing_data.get('series', []) + new_series
        else:
            # First batch
            all_series = new_series
        
        # Calculate statistics
        output_data = {
            'script': 'series_structure_analyzer',
            'analyzed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_series': len(all_series),
            'series_with_movies': len([s for s in all_series if s['has_filme']]),
            'total_movies': sum(s['movie_count'] for s in all_series),
            'total_episodes': sum(s['total_episodes'] for s in all_series),
            'total_content': sum(s['total_content'] for s in all_series),
            'processing_errors': existing_data.get('processing_errors', 0) if existing_data else 0,
            'series': all_series
        }
        
        # Save to file
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"   💾 Saved {len(all_series)} total series to database")
            return output_data
        except Exception as e:
            print(f"   ❌ Error saving data: {e}")
            return existing_data or {}
    
    def has_filme_endpoint(self, series_url: str) -> tuple[bool, int]:
        """Check if series has a filme page and count linked movies."""
        filme_url = series_url.rstrip('/') + '/filme'
        soup = self.get_soup(filme_url)
        if not soup:
            return False, 0

        movie_table = soup.find('table')
        if not movie_table:
            return False, 0

        movie_rows = movie_table.find_all('tr')
        movie_count = 0
        for row in movie_rows:
            if row.find('th'):
                continue
            if row.find('a', href=True):
                movie_count += 1

        return movie_count > 0, movie_count

    def get_season_numbers(self, soup: BeautifulSoup) -> List[int]:
        """Get available season numbers from the current page."""
        seasons_ul = self.find_labeled_list(soup, 'Staffeln:')
        if not seasons_ul:
            return []

        season_numbers = []
        for link in seasons_ul.find_all('a', href=True):
            text = link.get_text(strip=True)
            if text.isdigit():
                season_numbers.append(int(text))

        return sorted(set(season_numbers))

    def get_episode_endpoints_for_season(self, series_url: str, season_num: int) -> List[str]:
        """Get episode endpoints from a specific season page."""
        season_url = f"{series_url}/staffel-{season_num}"
        soup = self.get_soup(season_url)
        if not soup:
            return []

        table = soup.find('table')
        if not table:
            return []

        endpoints = []
        seen = set()

        for row in table.find_all('tr'):
            if row.find('th'):
                continue

            link = row.find('a', href=True)
            if not link:
                continue

            href = link.get('href', '')
            if '/episode-' not in href:
                continue

            endpoint = urljoin(config.BASE_URL, href)
            if '/serie/stream/' not in endpoint and '/serie/' in endpoint:
                endpoint = endpoint.replace('/serie/', '/serie/stream/', 1)

            if endpoint not in seen:
                seen.add(endpoint)
                endpoints.append(endpoint)

        return endpoints
    
    def analyze_series(self, series: Dict) -> Dict:
        """Analyze a single series structure"""
        series_url = self.normalize_series_url(series['url'])
        series_name = series['name']

        soup = self.get_soup(series_url)
        if not soup:
            return {
                'name': series_name,
                'url': series_url,
                'genre': series.get('genre', 'Unknown'),
                'has_filme': False,
                'movie_count': 0,
                'season_count': 0,
                'episode_counts': [],
                'total_episodes': 0,
                'total_content': 0,
                'endpoints': []
            }

        has_filme, movie_count = self.has_filme_endpoint(series_url)
        season_numbers = self.get_season_numbers(soup)
        episode_counts = []
        endpoints = []

        if has_filme and movie_count > 0:
            for i in range(1, movie_count + 1):
                endpoints.append(f"{series_url}/filme/film-{i}")

        for season_num in season_numbers:
            season_endpoints = self.get_episode_endpoints_for_season(series_url, season_num)
            episode_counts.append(len(season_endpoints))
            endpoints.extend(season_endpoints)
        
        return {
            'name': series_name,
            'url': series_url,
            'genre': series.get('genre', 'Unknown'),
            'has_filme': has_filme,
            'movie_count': movie_count,
            'season_count': len(season_numbers),
            'episode_counts': episode_counts,
            'total_episodes': sum(episode_counts),
            'total_content': movie_count + sum(episode_counts),
            'endpoints': endpoints
        }
    
    def run(self):
        """Run the series structure analysis"""
        # Check if batch processing is enabled
        if self.batch_size:
            print("🚀 Series Structure Analyzer (Batch Mode)")
            print(f"📂 Input: {self.input_file}")
            print(f"📂 Output: {self.output_file}")
            print(f"📊 Batch size: {self.batch_size}")
            if self.limit:
                print(f"📊 Total limit: {self.limit}")
            print("=" * 50)
            
            start_time = time.time()
            
            # Load series data
            series_list = self.load_series_data()
            if not series_list:
                print("❌ No series data found!")
                return False
            
            # Apply total limit if set
            if self.limit:
                series_list = series_list[:self.limit]
                print(f"📊 Limited to first {len(series_list)} series")
            
            # Load existing data to avoid duplicates
            existing_data = self.load_existing_data()
            existing_urls = self.get_existing_urls(existing_data)
            
            # Filter out already processed series
            remaining_series = [s for s in series_list if s['url'] not in existing_urls]
            
            if not remaining_series:
                print("✅ All series already processed!")
                return True
            
            print(f"📺 Processing {len(remaining_series)} remaining series in batches of {self.batch_size}")
            
            total_processed = 0
            errors = 0
            
            # Process in batches
            for batch_start in range(0, len(remaining_series), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(remaining_series))
                batch = remaining_series[batch_start:batch_end]
                batch_num = (batch_start // self.batch_size) + 1
                total_batches = (len(remaining_series) + self.batch_size - 1) // self.batch_size
                
                print(f"\n🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} series)")
                batch_start_time = time.time()
                
                analyzed_batch = []
                
                for i, series in enumerate(batch):
                    series_name = series.get('name', 'Unknown')
                    print(f"   📺 [{i+1}/{len(batch)}] Processing: {series_name}")
                    
                    try:
                        result = self.analyze_series(series)
                        analyzed_batch.append(result)
                        total_processed += 1
                        print(f"      ✅ Completed: {result['total_content']} content items ({result['movie_count']} movies, {result['total_episodes']} episodes)")
                            
                    except Exception as e:
                        errors += 1
                        print(f"      ❌ Error: {e}")
                        continue
                
                # Save batch results
                print(f"   💾 Saving batch {batch_num} results...")
                existing_data = self.save_batch_data(analyzed_batch, existing_data)
                
                batch_duration = time.time() - batch_start_time
                print(f"   ✅ Batch {batch_num} complete: {len(analyzed_batch)} series processed in {batch_duration:.1f}s")
                print(f"   📊 Progress: {total_processed}/{len(remaining_series)} series ({total_processed/len(remaining_series)*100:.1f}%)")
                
                # Show current totals
                current_total = existing_data.get('total_series', 0)
                print(f"   📈 Database now contains: {current_total} total series")
            
            total_duration = time.time() - start_time
            print(f"\n⚡ BATCH PROCESSING COMPLETE!")
            print(f"⏱️  Total time: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
            print(f"📊 Processed: {total_processed} series | Errors: {errors}")
            print(f"🎬 Final stats: {existing_data.get('series_with_movies', 0)} series with movies")
            print(f"📊 Final content: {existing_data.get('total_content', 0)} total items")
            
            return True
        
        else:
            # Original single-run processing
            print("🚀 Series Structure Analyzer")
            print(f"📂 Input: {self.input_file}")
            print(f"📂 Output: {self.output_file}")
            print("=" * 50)
            
            start_time = time.time()
            
            # Load series data
            series_list = self.load_series_data()
            if not series_list:
                print("❌ No series data found!")
                return False
            
            # Apply limit if set
            if self.limit:
                series_list = series_list[:self.limit]
                print(f"📺 Analyzing {len(series_list)} series (limit: {self.limit})...")
            else:
                print(f"📺 Analyzing {len(series_list)} series (no limit)...")
            
            analyzed_series = []
            processed = 0
            errors = 0
            
            for series in series_list:
                try:
                    result = self.analyze_series(series)
                    analyzed_series.append(result)
                    processed += 1
                    
                    # Progress indicator
                    if processed % 250 == 0 and processed > 0:
                        print(f"📊 {processed}/{len(series_list)}")
                    
                except Exception as e:
                    errors += 1
                    continue
            
            # Prepare output data
            output_data = {
                'script': 'series_structure_analyzer',
                'analyzed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_series': len(analyzed_series),
                'series_with_movies': len([s for s in analyzed_series if s['has_filme']]),
                'total_movies': sum(s['movie_count'] for s in analyzed_series),
                'total_episodes': sum(s['total_episodes'] for s in analyzed_series),
                'total_content': sum(s['total_content'] for s in analyzed_series),
                'processing_errors': errors,
                'series': analyzed_series
            }
            
            # Save results
            try:
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                
                duration = time.time() - start_time
                print(f"\n⚡ {duration:.1f}s | {len(analyzed_series)} analyzed | {errors} errors")
                print(f"🎬 {output_data['series_with_movies']} series with movies")
                print(f"📊 {output_data['total_content']} total content items")
                
                return True
                
            except Exception as e:
                print(f"❌ Error saving results: {e}")
                return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Series Structure Analyzer')
    parser.add_argument('--limit', type=int, help='Limit number of series to process')
    parser.add_argument('-b', '--batch', type=int, help='Batch processing size (e.g., -b 100)')
    args = parser.parse_args()
    
    print(f"DEBUG: limit={args.limit}, batch={args.batch}")
    
    analyzer = SeriesStructureAnalyzer(limit=args.limit, batch_size=args.batch)
    
    try:
        success = analyzer.run()
        print("✅ Analysis complete!" if success else "❌ Analysis failed!")
    except KeyboardInterrupt:
        print("🛑 Interrupted")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()
