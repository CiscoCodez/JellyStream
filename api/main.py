#!/usr/bin/env python3
"""Simple Streaming API for Jellyfin using SerienStream redirect data."""
import logging
import time
import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect, jsonify, request, Response
from urllib.parse import urljoin, urlparse
from data_loader import DataLoader
from redirector import RedirectResolver
from browser import PlaywrightRedirectResolver
from providers.voe import VOEProvider

# Configure logging to file (clears on restart)
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'streaming_api.log')

# Clear log file on startup
if os.path.exists(log_file):
    os.remove(log_file)

# Setup logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Global components
data_loader = None
redirect_resolver = None
browser_resolver = None
voe_provider = None
simple_cache = {}  # redirect_id -> {'stream_url': url, 'expires': timestamp, 'provider': str}
season_caching_locks = set()  # Track which seasons are being cached
CACHE_HOURS = 1  # 1 hour cache for HLS streams

def initialize_components():
    """Initialize shared API components for both Gunicorn and direct runs."""
    global data_loader, redirect_resolver, browser_resolver, voe_provider

    if (
        data_loader is not None
        and redirect_resolver is not None
        and browser_resolver is not None
        and voe_provider is not None
    ):
        return

    logging.info("Loading API components...")
    data_loader = DataLoader()
    redirect_resolver = RedirectResolver()
    browser_resolver = PlaywrightRedirectResolver()
    voe_provider = VOEProvider()
    data_loader.load()

def is_cache_valid(cache_entry):
    """Check if cache entry is still valid"""
    return cache_entry['expires'] > time.time()

def cache_stream(redirect_id, stream_url, provider_type):
    """Cache a resolved stream URL"""
    expires = time.time() + (CACHE_HOURS * 3600)
    simple_cache[redirect_id] = {
        'stream_url': stream_url,
        'expires': expires,
        'provider': provider_type
    }
    logging.info(f"📦 Cached {redirect_id} ({provider_type}) expires in {CACHE_HOURS}h")

def get_fresh_stream_url(episode_info, redirect_id):
    """Refresh the temporary SerienStream play URL from the episode page."""
    stored_stream_url = episode_info.get('stream_url')
    episode_url = episode_info.get('episode_data', {}).get('url')

    if not episode_url:
        return stored_stream_url

    try:
        response = requests.get(
            episode_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            timeout=15
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        for box in soup.select('button.link-box[data-link-id][data-play-url]'):
            if box.get('data-link-id') == str(redirect_id):
                play_url = box.get('data-play-url')
                if play_url:
                    fresh_url = urljoin('https://serienstream.to', play_url)
                    logging.info(f"Refreshed stream URL for {redirect_id}")
                    return fresh_url
    except Exception as e:
        logging.warning(f"Failed to refresh stream URL for {redirect_id}: {e}")

    return stored_stream_url


def resolve_provider_url(episode_info, redirect_id):
    """Resolve the provider URL for a redirect, preferring browser automation for supported sources."""
    source_site = episode_info.get('source_site', 'serienstream')
    episode_url = episode_info.get('episode_data', {}).get('url')
    fallback_stream_url = episode_info.get('stream_url')

    if browser_resolver and browser_resolver.can_handle_source(source_site):
        provider_url = browser_resolver.resolve_provider_url(
            source_site=source_site,
            episode_url=episode_url,
            redirect_id=str(redirect_id),
            fallback_stream_url=fallback_stream_url,
        )
        if provider_url:
            return provider_url
        logging.warning(
            "Browser resolver could not resolve %s for %s, falling back to HTTP redirect resolution",
            redirect_id,
            source_site,
        )

    stream_url = get_fresh_stream_url(episode_info, redirect_id)
    if not stream_url:
        return None
    return redirect_resolver.resolve_redirect(stream_url)

def _start_season_caching(episode_info, current_redirect_id):
    """Start background caching for the whole season"""
    try:
        series_idx = episode_info.get('series_idx')
        season_num = episode_info.get('season_num')
        
        if series_idx is None or season_num is None:
            return
        
        # Create unique lock key for this season
        season_lock_key = f"{series_idx}-{season_num}"
        
        # Check if this season is already being cached
        if season_lock_key in season_caching_locks:
            logging.info(f"🔄 Season {season_num} already being cached, skipping duplicate")
            return
        
        # Add lock to prevent duplicate caching
        season_caching_locks.add(season_lock_key)
        
        # Get all episodes in this season
        season_episodes = data_loader.get_season_episodes(series_idx, season_num)
        
        logging.info(f"🔄 Starting background caching for {len(season_episodes)} episodes in season {season_num}")
        
        # Start background thread to cache the season
        import threading
        thread = threading.Thread(
            target=_cache_season_background, 
            args=(season_episodes, current_redirect_id, season_lock_key),
            daemon=True
        )
        thread.start()
        
    except Exception as e:
        logging.error(f"Error starting season caching: {e}")

def _cache_season_background(season_episodes, skip_redirect_id, season_lock_key):
    """Background function to cache season episodes"""
    import time
    
    try:
        for episode in season_episodes:
            redirect_id = episode.get('redirect_id')
            
            # Skip the episode we just processed
            if redirect_id == skip_redirect_id:
                continue
            
            # Skip if already cached
            if redirect_id in simple_cache and is_cache_valid(simple_cache[redirect_id]):
                continue
            
            try:
                # Small delay to avoid overwhelming providers
                time.sleep(2)

                logging.info(f"🔄 Background caching: {redirect_id}")

                # Get episode info to determine site
                ep_info = data_loader.find_episode_by_redirect(redirect_id)
                if not ep_info:
                    continue

                provider_url = resolve_provider_url(ep_info, redirect_id)
                
                if provider_url:
                    provider_type = redirect_resolver.get_provider_type(provider_url)

                    # Always try VOE extraction
                    stream_url = voe_provider.extract_m3u8(provider_url)
                    if stream_url:
                        cache_stream(redirect_id, stream_url, provider_type)
                        logging.info(f"✅ Background cached: {redirect_id}")
                    
            except Exception as e:
                logging.error(f"Background caching error for {redirect_id}: {e}")
        
        logging.info("🏁 Background season caching completed")
        
    finally:
        # Always remove the lock when done
        season_caching_locks.discard(season_lock_key)

@app.route('/stream/direct/<redirect_id>')
def stream_direct(redirect_id):
    """Direct stream endpoint - sends 302 redirect to actual m3u8 URL for better Jellyfin compatibility"""
    try:
        logging.info(f"🎬 Direct stream request for redirect {redirect_id}")

        # Check cache first
        cached = simple_cache.get(redirect_id)
        if cached and is_cache_valid(cached):
            logging.info(f"📦 Cache hit for redirect {redirect_id} ({cached['provider']})")
            direct_url = cached['stream_url']
        else:
            logging.info(f"🔍 No cache found for {redirect_id}, resolving fresh...")

            # Find episode info
            episode_info = data_loader.find_episode_by_redirect(redirect_id)
            if not episode_info:
                return jsonify({"error": f"Redirect ID {redirect_id} not found"}), 404

            provider_url = resolve_provider_url(episode_info, redirect_id)

            if not provider_url:
                return jsonify({"error": "Failed to resolve stream URL"}), 500

            provider_type = redirect_resolver.get_provider_type(provider_url)
            logging.info(f"🎯 Provider: {provider_type}")

            # Extract VOE stream
            direct_url = voe_provider.extract_m3u8(provider_url)

            if direct_url:
                logging.info(f"✅ VOE stream extracted: {direct_url}")
                # Cache the result
                cache_stream(redirect_id, direct_url, provider_type)
                # Start background season caching
                _start_season_caching(episode_info, redirect_id)
            else:
                logging.warning("⚠️ VOE extraction failed")
                return jsonify({"error": "Failed to extract stream"}), 500

        # Return 302 redirect to the actual m3u8 URL
        logging.info(f"↪️  Redirecting to: {direct_url[:80]}...")
        return redirect(direct_url, code=302)

    except Exception as e:
        logging.error(f"❌ Error in stream_direct: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/stream/redirect/<redirect_id>')
def stream_redirect(redirect_id):
    """Main streaming endpoint - returns M3U8 with absolute URLs"""
    try:
        logging.info(f"🎬 Stream request for redirect {redirect_id}")

        # Check cache first
        cached = simple_cache.get(redirect_id)
        if cached and is_cache_valid(cached):
            logging.info(f"📦 Cache hit for redirect {redirect_id} ({cached['provider']})")
            direct_url = cached['stream_url']
        else:
            logging.info(f"🔍 No cache found for {redirect_id}, resolving fresh...")
            
            # Find episode info
            episode_info = data_loader.find_episode_by_redirect(redirect_id)
            if not episode_info:
                logging.warning(f"❌ Redirect ID {redirect_id} not found in data")
                return jsonify({'error': 'Redirect ID not found'}), 404

            source_site = episode_info.get('source_site', 'serienstream')
            logging.info(f"🔍 Resolving {redirect_id} ({source_site}) for {episode_info['series_name']} S{episode_info['season_num']}E{episode_info['episode_num']}")
            
            # Step 1: Get the direct provider URL
            provider_url = resolve_provider_url(episode_info, redirect_id)
            
            if not provider_url:
                logging.error(f"❌ Failed to resolve redirect {redirect_id}")
                return jsonify({'error': 'Failed to resolve stream URL'}), 503
            
            provider_type = redirect_resolver.get_provider_type(provider_url)
            logging.info(f"🔍 Provider detected: {provider_type} - URL: {provider_url}")

            # Step 2: Always try VOE extraction (they change domains constantly)
            logging.info("🎯 Attempting VOE extraction...")
            direct_url = voe_provider.extract_m3u8(provider_url)

            if direct_url:
                logging.info(f"✅ VOE stream extracted: {direct_url}")
                # Cache the result
                cache_stream(redirect_id, direct_url, provider_type)
                # Start background season caching
                _start_season_caching(episode_info, redirect_id)
            else:
                logging.warning("⚠️ VOE extraction failed, falling back to direct URL")
                return redirect(provider_url)
        
        # Now we have the direct VOE URL, let's fetch and fix the M3U8 content
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://jilliandescribecompany.com/'
            }
            
            response = requests.get(direct_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            content = response.text
            logging.info(f"📄 Fetched M3U8 content: {len(content)} chars")
            
            # Parse the base URL from the direct_url
            parsed = urlparse(direct_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}{'/'.join(parsed.path.split('/')[:-1])}/"
            
            # Convert relative URLs to absolute URLs
            lines = content.split('\n')
            fixed_lines = []
            fixed_count = 0
            
            for line in lines:
                if line and not line.startswith('#') and ('.' in line):
                    # This is a URL line - make it absolute
                    if not line.startswith('http'):
                        absolute_url = urljoin(base_url, line.strip())
                        fixed_lines.append(absolute_url)
                        fixed_count += 1
                        logging.info(f"🔧 Fixed URL: {line.strip()[:50]}... → absolute URL")
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            
            fixed_content = '\n'.join(fixed_lines)
            logging.info(f"✅ Fixed {fixed_count} relative URLs to absolute URLs")
            
            # Return the fixed M3U8 content
            return Response(
                fixed_content,
                mimetype='application/vnd.apple.mpegurl',
                headers={
                    'Content-Type': 'application/vnd.apple.mpegurl',
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'no-cache'
                }
            )
            
        except Exception as e:
            logging.error(f"❌ Error processing M3U8 content: {e}")
            # Fallback to direct redirect
            return redirect(direct_url)
        
    except Exception as e:
        logging.error(f"❌ Error resolving redirect {redirect_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    # Clean expired cache entries
    current_time = time.time()
    expired_keys = [k for k, v in simple_cache.items() if v['expires'] <= current_time]
    for key in expired_keys:
        del simple_cache[key]
    
    if expired_keys:
        logging.info(f"🧹 Cleaned {len(expired_keys)} expired cache entries")
    
    # Count cache by provider
    cache_by_provider = {}
    for entry in simple_cache.values():
        provider = entry.get('provider', 'unknown')
        cache_by_provider[provider] = cache_by_provider.get(provider, 0) + 1
    
    return jsonify({
        'status': 'healthy',
        'cache_size': len(simple_cache),
        'cache_by_provider': cache_by_provider,
        'cache_cleaned': len(expired_keys),
        'cache_duration_hours': CACHE_HOURS,
        'series_count': data_loader.get_series_count() if data_loader else 0,
        'redirect_count': data_loader.get_redirect_count() if data_loader else 0,
        'log_file': log_file
    })

@app.route('/info/<redirect_id>')
def redirect_info(redirect_id):
    """Get info about a redirect ID (for debugging)"""
    episode_info = data_loader.find_episode_by_redirect(redirect_id)
    if not episode_info:
        return jsonify({'error': 'Redirect ID not found'}), 404
    
    # Add cache info if available
    cached = simple_cache.get(redirect_id)
    if cached:
        episode_info['cached'] = {
            'stream_url': cached['stream_url'],
            'provider': cached['provider'],
            'expires_in': int(cached['expires'] - time.time())
        }
    
    return jsonify(episode_info)

@app.route('/test/<redirect_id>')
def test_redirect(redirect_id):
    """Test redirect resolution without caching (for debugging)"""
    try:
        # Get episode info to determine source site
        episode_info = data_loader.find_episode_by_redirect(redirect_id)
        redirect_url = get_fresh_stream_url(episode_info, redirect_id)
        logging.info(f"🧪 Testing redirect resolution for {redirect_id} ({episode_info.get('source_site', 'serienstream')})")

        # Step 1: Resolve redirect
        provider_url = resolve_provider_url(episode_info, redirect_id)
        if not provider_url:
            return jsonify({'error': 'Failed to resolve redirect', 'step': 'redirect_resolution'})
        
        provider_type = redirect_resolver.get_provider_type(provider_url)
        
        result = {
            'redirect_id': redirect_id,
            'redirect_url': redirect_url,
            'provider_url': provider_url,
            'provider_type': provider_type,
            'stream_url': None,
            'extraction_method': None
        }
        
        # Step 2: Extract stream URL (VOE only)
        if provider_type == 'voe' and voe_provider.can_handle(provider_url):
            stream_url = voe_provider.extract_m3u8(provider_url)
            result['stream_url'] = stream_url
            result['extraction_method'] = 'voe_provider'
        else:
            result['stream_url'] = provider_url
            result['extraction_method'] = 'direct_fallback'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e), 'step': 'exception'}), 500

@app.route('/stats')
def stats():
    """Get API statistics"""
    if not data_loader:
        return jsonify({'error': 'Data not loaded'}), 500
    
    return jsonify(data_loader.get_stats())

@app.route('/clear-cache')
def clear_cache():
    """Clear all cached streams"""
    global simple_cache
    cache_count = len(simple_cache)
    simple_cache.clear()
    logging.info(f"🧹 Cleared {cache_count} cache entries")
    return jsonify({'message': f'Cleared {cache_count} cache entries'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def main():
    
    print("🚀 Starting VOE-focused Streaming API...")
    logging.info("🚀 Starting VOE-focused Streaming API...")
    
    # Initialize components
    print("📁 Loading series data...")
    logging.info("📁 Loading series data...")
    
    print("🔧 Initializing redirect resolver...")
    logging.info("🔧 Initializing redirect resolver...")
    
    print("🎬 Initializing VOE provider...")
    logging.info("🎬 Initializing VOE provider...")
    
    try:
        initialize_components()
        stats_data = data_loader.get_stats()

        print(f"✅ Loaded {data_loader.get_series_count()} series with {data_loader.get_redirect_count()} streams")
        logging.info(f"✅ Loaded {data_loader.get_series_count()} series with {data_loader.get_redirect_count()} streams")

        # Show loaded sites
        print(f"📁 Loaded {len(stats_data['sites'])} site(s):")
        logging.info(f"📁 Loaded {len(stats_data['sites'])} site(s):")
        for site_name, site_info in stats_data['sites'].items():
            print(f"   - {site_name}: {site_info['series_count']} series")
            logging.info(f"   - {site_name}: {site_info['series_count']} series")

        # Show some stats
        print(f"📊 Providers: {stats_data['providers']}")
        print(f"🌍 Languages: {stats_data['languages']}")
        print(f"🔄 Redirect resolver ready with SSL bypass")
        print(f"🎯 VOE provider ready with deobfuscation")
        print(f"⏰ Cache duration: {CACHE_HOURS} hour(s)")
        print(f"📝 Logging to: {log_file}")
        
        logging.info(f"📊 Providers: {stats_data['providers']}")
        logging.info(f"🌍 Languages: {stats_data['languages']}")
        logging.info(f"🔄 Redirect resolver ready with SSL bypass")
        logging.info(f"🎯 VOE provider ready with deobfuscation")
        logging.info(f"⏰ Cache duration: {CACHE_HOURS} hour(s)")
        logging.info(f"📝 Logging to: {log_file}")
        
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        logging.error(f"❌ Failed to load data: {e}")
        return
    
    print("🌐 Starting Flask server on http://localhost:3000")
    print("📋 Available endpoints:")
    print("   GET /stream/redirect/<id>  - Main streaming endpoint")
    print("   GET /health                - Health check")
    print("   GET /info/<id>             - Debug info for redirect")
    print("   GET /test/<id>             - Test redirect resolution")
    print("   GET /stats                 - API statistics")
    print("   GET /clear-cache           - Clear all cached streams")
    print("   Example: http://localhost:3000/stream/redirect/11050650")
    
    logging.info("🌐 Starting Flask server on http://localhost:3000")
    logging.info("📋 Available endpoints:")
    logging.info("   GET /stream/redirect/<id>  - Main streaming endpoint")
    logging.info("   GET /health                - Health check")
    logging.info("   GET /info/<id>             - Debug info for redirect")
    logging.info("   GET /test/<id>             - Test redirect resolution")
    logging.info("   GET /stats                 - API statistics")
    logging.info("   GET /clear-cache           - Clear all cached streams")
    logging.info("   Example: http://localhost:3000/stream/redirect/11050650")
    
    # Start server
    app.run(
        host='0.0.0.0',
        port=3000,
        debug=False,
        threaded=True
    )

initialize_components()

if __name__ == '__main__':
    main()
