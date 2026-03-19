# SerienStream Project - Roadmap & TODO

## Current Status

### Completed Features ✅

#### Core Infrastructure
- [x] Series catalog scraper (10,276 series)
- [x] Season/episode structure scraper
- [x] Stream URL scraper (English-only export)
- [x] JSON database structurer
- [x] Database updater (incremental updates)
- [x] Jellyfin folder structure generator
- [x] Streaming API with Flask
- [x] VOE provider integration
- [x] HLS stream caching (1 hour TTL)
- [x] Systemd service support for API
- [x] Jellyfin stack overflow fix (8MB thread stack)
- [x] Jellyfin plugin for in-app updates

#### Data Collection
- [x] **10,276 series** indexed
- [x] **286,428 episodes** scraped
- [x] **1,751 movies** scraped
- [x] **67,685 English stream redirects** cataloged
- [x] English-only export pipeline
- [x] Multiple hosting providers per episode

#### Jellyfin Integration
- [x] .strm file generation
- [x] Language prioritization (English only)
- [x] Large library support (10,000+ series without crash)
- [x] Automated folder structure
- [x] Plugin-based series search and update

---

#### Project Consolidation (March 2026)
- [x] **Single-site architecture** - SerienStream only
- [x] **API cleanup** - SerienStream-only data loading
- [x] **Plugin cleanup** - SerienStream-only search/update flow
- [x] **Documentation cleanup** - Markdown aligned with current architecture

---

## In Progress 🚧

### Deployment Hardening
**Status:** Core functionality is stable, deployment polish is ongoing

**Active Work:**
- [ ] Finalize production deployment checklist
- [ ] Standardize VPS paths and service names
- [ ] Review plugin repository metadata before release
- [ ] Validate clean install on a fresh Jellyfin VPS

**Priority:** High

---

## Planned Features 📋

### High Priority

#### 1. Automatic Database Updates
**Goal:** Keep the SerienStream database fresh with daily or weekly updates

**Tasks:**
- [ ] Create cron job or systemd timer for `5_updater.py`
- [ ] Add change detection (new episodes, new series)
- [ ] Implement incremental Jellyfin updates
  - Only regenerate changed series
  - Trigger partial library scan
- [ ] Add update notifications
  - Log new content
  - Send webhook/email on updates

**Schedule:**
- Daily: Check for new episodes
- Weekly: Full database refresh
- Monthly: Cleanup dead links

**Estimated Effort:** 1 week

---

#### 2. Multi-Provider Support
**Goal:** Improve reliability with stronger provider fallback beyond the current VOE-focused flow

**Providers to Improve:**
- [ ] Streamtape
- [ ] Vidoza
- [ ] Doodstream
- [ ] Upstream

**Tasks:**
- [ ] Expand provider modules
- [ ] Add provider fallback logic
- [ ] Test stream quality and reliability
- [ ] Add provider preference to config

**Benefits:**
- Better reliability (fallback if one provider is down)
- Faster streams (can choose fastest provider)
- Less dependence on single provider path

**Estimated Effort:** 1-2 weeks

---

#### 3. FlareSolverr Integration (Future/If Needed)
**Status:** Removed for now - not needed as direct requests work

**If Cloudflare blocking occurs in future:**
- [ ] Re-implement FlareSolverr client library
- [ ] Add smart request handler with automatic fallback
- [ ] Integrate into scrapers 1-3
- [ ] Add fallback to api/redirector.py

**Priority:** Low (only if site starts blocking)

---

### Medium Priority

#### 4. Enhanced API Features

**Tasks:**
- [ ] Add search endpoint (`/search?q=series+name`)
- [ ] Add random episode endpoint (`/random`)
- [ ] Add recently added endpoint (`/recent`)
- [ ] Add provider status endpoint (`/providers/status`)
- [ ] Add stream quality selection
- [ ] Add subtitle support

**Estimated Effort:** 1 week

---

#### 5. Web Dashboard
**Goal:** Monitor and manage the system via web UI

**Features:**
- [ ] API statistics dashboard
- [ ] Database status (series count, last update)
- [ ] Provider health monitoring
- [ ] Manual update triggers
- [ ] Search interface
- [ ] Stream testing tool

**Tech Stack:** React or vanilla JS + Flask backend

**Estimated Effort:** 2-3 weeks

---

#### 6. Performance Optimizations

**Tasks:**
- [ ] Database indexing for faster lookups
- [ ] Redis caching layer
  - Cache redirect resolutions
  - Cache provider responses
- [ ] Parallel scraping (multiprocessing)
- [ ] Optimize Jellyfin structure generation
  - Incremental updates only
  - Skip unchanged series

**Estimated Effort:** 1-2 weeks

---

### Low Priority

#### 7. Subtitles Integration
**Goal:** Download and serve subtitles for episodes

**Tasks:**
- [ ] Scrape subtitle URLs from SerienStream
- [ ] Download and store .srt files
- [ ] Serve subtitles via API
- [ ] Add subtitle paths to .strm metadata

**Estimated Effort:** 2 weeks

---

#### 8. Quality Metrics
**Goal:** Track stream quality and reliability

**Tasks:**
- [ ] Log stream success/failure rates
- [ ] Track buffering/loading times
- [ ] Provider uptime monitoring
- [ ] Quality reports (weekly/monthly)

**Estimated Effort:** 1 week

---

#### 9. Mobile App (Future)
**Goal:** Native mobile app for browsing or streaming

**Features:**
- Browse series catalog
- Search functionality
- Direct streaming (bypass Jellyfin)
- Download for offline viewing

**Tech Stack:** React Native or Flutter

**Estimated Effort:** 6-8 weeks

---

## Technical Debt 🔧

### Code Quality
- [ ] Add comprehensive logging
- [ ] Add error handling and retries
- [ ] Write unit tests for scrapers
- [ ] Write integration tests for API
- [ ] Add type hints (Python 3.10+)
- [ ] Code documentation (docstrings)

### Infrastructure
- [ ] Set up proper backup system
  - Backup database daily
  - Backup configuration
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Set up alerting (failed scrapes, API errors)
- [ ] Docker/Docker Compose support
- [ ] CI/CD pipeline

### Security
- [ ] Add API authentication (API keys)
- [ ] Rate limiting on API endpoints
- [ ] Input validation and sanitization
- [ ] HTTPS support
- [ ] Secrets management (env vars)

---

## Feature Requests 💡

Have a feature idea? Add it here!

### Community Requests
- [ ] Support for other streaming sites (suggestions welcome)
- [ ] Bulk download support
- [ ] Watchlist/favorites system
- [ ] Episode progress tracking
- [ ] Multi-user support

---

## Completed Milestones 🎉

### v1.0 - Initial Release (June 2024)
- ✅ Full scraping pipeline
- ✅ JSON database
- ✅ VOE provider support

### v1.1 - Jellyfin Integration (November 2024)
- ✅ Jellyfin structure generator
- ✅ Streaming API
- ✅ 10,000+ series support
- ✅ Stack overflow fix for large libraries

### v1.2 - SerienStream Consolidation (March 2026)
- ✅ SerienStream-only architecture
- ✅ English-only export pipeline
- ✅ Plugin cleanup
- ✅ Documentation refresh

---

## Next Release: v1.3 - Deployment & Automation (2026)

**Target Date:** TBD

**Goals:**
- [ ] Production deployment guide finalized
- [ ] Automated update workflow
- [ ] Cleaner release packaging
- [ ] Broader provider fallback

---

## Long-term Vision 🚀

**Year 1:**
- Improve deployment reliability
- Add provider fallback improvements
- Build web dashboard
- Implement automatic updates

**Year 2:**
- Mobile app development
- Advanced features (subtitles, quality selection)
- Community features (watchlists, ratings)
- Optional expansion beyond SerienStream if needed

**Ultimate Goal:**
- Unified self-hosted streaming platform for SerienStream content
- Smooth Jellyfin integration
- Reliable updates and playback
- High reliability and performance

---

## Contributing

Want to help? Pick a task from the TODO list and get started!

**Priority order:**
1. Automatic Updates (maintenance)
2. Multi-Provider Support (reliability)
3. Deployment Hardening (operations)
4. Web Dashboard (UX improvement)

---

*Last Updated: March 2026*
