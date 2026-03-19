# JellyStream

A unified platform for streaming SerienStream content through Jellyfin, with automated scraping, English-dub filtering, and a streaming API backend.

## Overview

JellyStream scrapes SerienStream for TV series metadata, filters the database to English-dubbed streams only, generates Jellyfin-compatible folder structures with .strm files, and provides a streaming API to serve the content.

### Current Status

**SerienStream** (Series): ✅ Implemented
- **10,276 series** indexed
- **286,428 episodes** + **1,751 movies**
- **67,685 English stream redirects** cataloged
- **Providers:** VOE, Vidoza, Doodstream
- **Languages:** English only

**FlareSolverr Integration**: 🚧 In Progress
- Cloudflare bypass for protected sites
- Currently being evaluated for future-proofing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Source Site                              │
│                    serienstream.to                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              SerienStream Scraping Pipeline                 │
│  sites/serienstream/                                        │
│  1. Catalog Scraper                                         │
│  2. Season/Episode                                          │
│  3. Language/Streams                                        │
│  4. JSON Structurer                                         │
│  → final_series_data.json                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Jellyfin Structure Generator                   │
│  - Creates folder hierarchy for SerienStream                │
│  - Generates .strm files with redirect IDs                  │
│  - Uses English-only language priority                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Streaming API                             │
│  - Flask-based API                                          │
│  - Loads SerienStream database                              │
│  - VOE-focused extraction with redirect fallback            │
│  - HLS stream caching (1 hour)                              │
│  - Default endpoint: http://localhost:3000                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    Jellyfin Server                          │
│  - Single SerienStream library                              │
│  - Plays .strm files via local API                          │
│  - Stack fix available for large libraries                  │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
JellyStream/
├── README.md                  # This file
│
├── sites/                     # Site-specific scrapers
│   └── serienstream/          # SerienStream pipeline
│       ├── 1_catalog_scraper.py
│       ├── 2_url_season_episode_num.py
│       ├── 3_language_streamurl.py
│       ├── 4_json_structurer.py
│       ├── 5_updater.py
│       ├── 6_main.py
│       ├── 7_jellyfin_structurer.py
│       ├── config.py         # Site-specific config
│       └── data/
│           └── final_series_data.json
│
├── api/                      # Streaming API
│   ├── main.py              # Flask server
│   ├── data_loader.py       # SerienStream data loader
│   ├── redirector.py        # Redirect resolver
│   ├── providers/           # Streaming providers
│   │   ├── voe.py          # VOE extractor
│   │   └── vidoza.py       # Vidoza helper
│   └── downloader/
│       └── voe_dl.py       # VOE direct downloader
│
├── utils/                   # Shared utilities
│   └── manual_updater.py   # Interactive CLI for updating series
│
├── plugin/                  # Jellyfin plugin (optional)
│   └── JellyStream/        # Native Jellyfin plugin for UI-based updates
│       ├── Api/            # REST API controllers
│       ├── Configuration/  # Plugin settings and web UI
│       └── README.md       # Plugin documentation
│
├── tools/                   # Local maintenance helpers
│   └── filter_serienstream_english.py
│
└── docs/                    # Documentation
    ├── TODO.md             # Project roadmap
    ├── JELLYFIN_METADATA_CLEANUP.md
    └── JELLYFIN_STACK_FIX.md
```

## Components

### 1. SerienStream Scrapers

The SerienStream pipeline in `sites/serienstream/` follows this flow:

1. **1_catalog_scraper.py** - Scrapes catalog (name, URL, year)
2. **2_url_season_episode_num.py** - Gets season/episode structure
3. **3_language_streamurl.py** - Fetches stream URLs and keeps English streams only
4. **4_json_structurer.py** - Combines into final database
5. **5_updater.py** - Updates database with new content
6. **6_main.py** - Runs full pipeline
7. **7_jellyfin_structurer.py** - Generates Jellyfin folder structure

**Site Config:**
- `config.py` - SerienStream settings (URL, language priority, providers, paths)

### 2. Streaming API

Located in `api/`:

**Core Files:**
- `main.py` - Flask API server
- `data_loader.py` - Loads SerienStream database
- `redirector.py` - Resolves stream redirects
- `providers/*.py` - Provider-specific stream extractors

**Endpoints:**
- `GET /stream/redirect/<id>` - Main streaming endpoint
- `GET /health` - API health check
- `GET /stats` - API statistics
- `GET /info/<id>` - Debug info for redirect ID
- `GET /test/<id>` - Test redirect resolution
- `GET /clear-cache` - Clear stream cache

**Behavior:**
- Loads SerienStream data only
- Uses English-only redirect selection for season caching
- Serves redirects from `serienstream.to`

### 3. Jellyfin Integration

**SerienStream Library:**
- Media directory: `/media/jellyfin/serienstream/`
- Structure: `Series Name (Year)/Season XX/Episode.strm`
- .strm files point to: `http://localhost:3000/stream/redirect/[id]`

**Stack Overflow Fix:**
For large libraries (8,000+ series), apply Jellyfin stack fix:
```bash
mkdir -p /etc/systemd/system/jellyfin.service.d
cat > /etc/systemd/system/jellyfin.service.d/stack-size.conf << 'EOF'
[Service]
Environment="DOTNET_DefaultStackSize=8000000"
Environment="COMPlus_DefaultStackSize=8000000"
LimitSTACK=infinity
EOF

systemctl daemon-reload
systemctl restart jellyfin
```

See [docs/JELLYFIN_STACK_FIX.md](docs/JELLYFIN_STACK_FIX.md) for details.

### 4. Jellyfin Plugin (Optional)

A native Jellyfin plugin is available for updating SerienStream series directly from the Jellyfin UI without using the command line.

**Features:**
- 🔍 Search SerienStream series
- 🔄 Update individual series with latest episodes
- 📊 Real-time log streaming during updates
- 🔒 Secure (requires admin authentication)

**Installation:**

Via Jellyfin Repository (Recommended):
1. Dashboard → Plugins → Repositories
2. Add: `https://raw.githubusercontent.com/Macro002/JellyStream/main/manifest.json`
3. Catalog → Install "JellyStream"
4. Restart Jellyfin

See [plugin/README.md](plugin/README.md) for detailed documentation, manual installation, and configuration.

## Quick Start

### Prerequisites

- Python 3.11+
- Jellyfin server
- 200MB+ disk space for database files

### 1. Install Dependencies

```bash
pip3 install flask requests beautifulsoup4
```

### 2. Run Scrapers

```bash
cd sites/serienstream

# Test with small sample
python3 6_main.py --limit 10

# Full scrape
python3 6_main.py
```

### 3. Generate Jellyfin Structure

```bash
cd sites/serienstream
python3 7_jellyfin_structurer.py --api-url http://localhost:3000/stream/redirect
```

### 4. Start Streaming API

```bash
cd api
python3 main.py

# Or install as systemd service (recommended)
# See deployment section below
```

### 5. Add Library to Jellyfin

1. Open Jellyfin
2. Go to: Dashboard → Libraries → Add Library
3. Content type: TV Shows
4. Folder: `/media/jellyfin/serienstream`
5. Disable metadata downloads (recommended for performance)
6. Scan library

## Usage

### Update Series Database

```bash
cd sites/serienstream

# Update with new episodes only
python3 5_updater.py

# Full re-scrape
python3 6_main.py
```

### Monitor Streaming API

```bash
# Check API health
curl http://localhost:3000/health

# View statistics
curl http://localhost:3000/stats

# Test specific redirect
curl http://localhost:3000/test/<redirect_id>
```

## Deployment (Production)

### Deploy API as Systemd Service

```bash
# Copy project to /opt
sudo cp -r /path/to/JellyStream /opt/JellyStream

# Create systemd service
sudo cat > /etc/systemd/system/jellystream-api.service << 'EOF'
[Unit]
Description=JellyStream API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/JellyStream/api
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 /opt/JellyStream/api/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable jellystream-api
sudo systemctl start jellystream-api
sudo systemctl status jellystream-api
```

## Data Structure

### SerienStream Database Format

The pipeline produces a `final_series_data.json` file:

```json
{
  "series": [
    {
      "name": "Series Name",
      "jellyfin_name": "Series Name (2020)",
      "url": "https://serienstream.to/serie/stream/...",
      "seasons": {
        "season_1": {
          "episodes": {
            "episode_1": {
              "streams_by_language": {
                "Englisch": [
                  {
                    "provider": "VOE",
                    "stream_url": "https://serienstream.to/redirect/xyz123"
                  }
                ]
              }
            }
          }
        }
      }
    }
  ]
}
```

### Language Priority

**SerienStream:**
1. Englisch (English audio)

### Provider Priority

**SerienStream:** VOE → Vidoza → Doodstream

## Performance

### Scraping
- **Catalog:** ~2-3 requests/sec
- **Episodes:** ~1-2 requests/sec
- **Full scrape (10K series):** several hours

### API
- **Direct redirects:** <100ms
- **Stream resolution:** 1-3 seconds (cached 1 hour)
- **Concurrent streams:** 50-100 simultaneous

### Jellyfin Scan
- **Small (<1K series):** 5-15 minutes
- **Large (10K+ series):** 2-6 hours (requires stack fix)

## Troubleshooting

### API Won't Start

```bash
# Check if data file exists
ls sites/serienstream/data/final_series_data.json

# Test data loader manually
cd api
python3 -c "from data_loader import DataLoader; loader = DataLoader(); loader.load()"
```

### Scrapers Fail

```bash
# Check site availability
curl https://serienstream.to

# Test with small limit first
python3 6_main.py --limit 5
```

### Jellyfin Stack Overflow

Apply stack fix (see Quick Start section 3 or [docs/JELLYFIN_STACK_FIX.md](docs/JELLYFIN_STACK_FIX.md))

### Streams Not Playing

```bash
# Verify API is running
curl http://localhost:3000/health

# Test specific redirect
curl http://localhost:3000/test/<redirect_id>

# Check API logs
tail -f api/streaming_api.log
```

## Future Plans

See [docs/TODO.md](docs/TODO.md) for detailed roadmap.

**In Progress:**
- FlareSolverr evaluation for Cloudflare bypass
- Deployment hardening for VPS/Jellyfin environments

**Planned:**
- Additional provider support
- Automatic daily updates
- Web dashboard for monitoring
- Stream health checking and auto-updates

## License

Personal project - Use at your own risk.

## Disclaimer

This project is for educational purposes. Ensure you comply with all applicable laws and terms of service when using this software.
