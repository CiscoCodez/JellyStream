# JellyStream Plugin

A Jellyfin plugin for searching and updating SerienStream series.

## Features

- 🔍 Search for SerienStream series
- 🔄 Update individual series with latest episodes
- 📊 Real-time log streaming during updates
- ⚡ Live progress updates in the UI
- 🎯 Simple and clean interface
- **English-Only Workflow**: Matches the SerienStream English-dub pipeline

## Building the Plugin

### Prerequisites

- .NET 8.0 SDK
- Jellyfin 10.9.x
- Python 3.11+ with dependencies (already installed on Jellyfin server)
- JellyStream project at /opt/JellyStream on Jellyfin server

### Build Steps

```bash
cd plugin/JellyStream
dotnet restore
dotnet build --configuration Release
```

This will create a DLL at: `bin/Release/net8.0/JellyStream.dll`

## Installation

### Method 1: Via Jellyfin Repository (Recommended)

1. Open Jellyfin Dashboard → Plugins → Repositories
2. Add repository URL: `https://raw.githubusercontent.com/Macro002/JellyStream/main/manifest.json`
3. Go to Catalog
4. Find "JellyStream" and click Install
5. Restart Jellyfin

### Method 2: Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/Macro002/JellyStream/releases)
2. Extract to your Jellyfin plugins folder: `/var/lib/jellyfin/plugins/JellyStream/`
3. Restart Jellyfin

## Configuration

After installation, go to Jellyfin Dashboard → Plugins → JellyStream:

- **Script Path**: Path to the manual_updater.py script (default: `/opt/JellyStream/utils/manual_updater.py`)

## Usage

1. Navigate to Plugins → JellyStream
2. Enter series name and click Search
3. Click Update on any series to update it
4. Watch the live logs as the update progresses

## How It Works

### Architecture

The plugin is a **thin wrapper** around `manual_updater.py`:

```
Jellyfin UI → Plugin API → manual_updater.py → Database + .strm files
```

### Update Flow

1. User searches for series in Jellyfin plugin UI
2. Plugin calls: `python3 manual_updater.py --plugin --site serienstream --search "query"`
3. User clicks "Update" on a series
4. Plugin calls: `python3 manual_updater.py --plugin --site serienstream --series-name "Name" --json`
5. `manual_updater.py` handles everything:
   - Runs Python scraper scripts (2, 3, 4)
   - Updates database
   - Regenerates .strm files
   - Returns JSON result
6. Plugin parses JSON and shows result

### Files

- **Plugin**: `/var/lib/jellyfin/plugins/JellyStream_1.0.0.0/` (C#)
- **Script**: `/opt/JellyStream/utils/manual_updater.py` (Python)
- **Scrapers**: `/opt/JellyStream/sites/serienstream/` (Python)
- **Database**: `/opt/JellyStream/sites/serienstream/data/final_series_data.json`
- **Media**: `/media/jellyfin/serienstream/` (.strm files)

## Development

### Project Structure

```
JellyStream/
├── Plugin.cs                      # Main plugin entry point
├── Configuration/
│   └── PluginConfiguration.cs     # Settings model (paths)
├── Api/
│   ├── SeriesController.cs        # Search endpoint → calls manual_updater.py
│   └── UpdateController.cs        # Update endpoint → calls manual_updater.py
└── Web/
    ├── index.html                 # Plugin UI
    ├── jellystream.js             # Frontend logic
    └── jellystream.css            # Styling
```

### API Endpoints

- `GET /JellyStream/Series/Search?site=serienstream&query={text}` - Search for series
- `POST /JellyStream/Update/Series?name={name}&site=serienstream` - Update a series
- `GET /JellyStream/Update/Logs?key={logKey}` - Get live update logs

Both update endpoints call `manual_updater.py` with SerienStream-specific flags.

## Requirements

- Jellyfin 10.9.0 or higher
- Python 3.x
- JellyStream manual_updater.py script installed at `/opt/JellyStream/utils/manual_updater.py`

## Troubleshooting

**Plugin doesn't appear in Jellyfin:**
- Check Jellyfin logs: `/var/log/jellyfin/`
- Verify .NET 8.0 is installed
- Ensure file permissions are correct

**Update fails:**
- Check that the script path is correct in plugin settings
- Verify network connectivity to serienstream.to
- Check Jellyfin logs for detailed error messages
- Watch the live logs in the UI for specific errors

## License

Part of the JellyStream project.
