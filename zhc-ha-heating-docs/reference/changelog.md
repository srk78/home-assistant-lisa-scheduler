---
title: Changelog
tags: [reference, changelog]
---

# Changelog

All notable changes to the ZHC Heating Scheduler.

## [0.2.0] - 2024-11-26

### Added - Configurable Scraper System

- ✨ **Configurable scraper** - No code changes needed!
- ✨ **Multiple source support** - Training + matches from different URLs
- ✨ **CSS selector configuration** - Configure via YAML/UI
- ✨ **API and iCal support** - Built-in support for different source types
- ✨ **Configuration validator** - Validates configuration with helpful errors
- ✨ **Scraper config testing** - Test configurations before going live

### Added - Documentation Overhaul

- 📚 **Obsidian-style documentation** - Organized `docs/` folder
- 📚 **UI installation guide** - Step-by-step for beginners
- 📚 **Scraper configuration guide** - Configure without coding
- 📚 **Wiki-style cross-linking** - Easy navigation
- 📚 **Comprehensive index** - Clear starting points
- 📚 **Example configurations** - Real-world setups

### Changed

- 🔧 **Coordinator** - Now supports configurable scrapers
- 🔧 **Constants** - Added scraper configuration options
- 🔧 **Root README** - Simplified, points to docs

### Technical

- New file: `configurable_scraper.py` - Flexible scraper implementation
- New file: `scraper_config_validator.py` - Configuration validation
- Updated: `coordinator.py` - Support for configurable scraper
- Updated: `const.py` - Scraper configuration constants

## [0.1.0] - 2024-11-24

### Added - Initial Release

- ✅ **Core Integration**
  - Home Assistant custom component
  - Config flow for UI configuration
  - YAML configuration support
  
- ✅ **Schedule Scraping**
  - Generic HTML parser
  - BeautifulSoup4-based scraping
  - Multiple parsing strategies
  - ZHC custom scraper example

- ✅ **Heating Control**
  - Pre-heat time calculation
  - Cool-down period support
  - Heating window generation
  - Overlapping event merging
  - Plugwise SA integration

- ✅ **Sensors**
  - Next heating start/stop times
  - Current event details
  - Events today count
  - Heating minutes today
  - Total heating windows
  - Last schedule update
  - Heating active status
  - Scheduler enabled status
  - Manual override status

- ✅ **Services**
  - Refresh schedule
  - Enable/disable scheduler
  - Set/clear manual override

- ✅ **Features**
  - Dry run mode for testing
  - Manual override capability
  - Error recovery
  - State restoration
  - Debug logging

- ✅ **Documentation**
  - README with features
  - Quick start guide
  - Configuration guide
  - Scraper guide
  - Development guide
  - ZHC-specific setup

- ✅ **Testing**
  - Unit tests for scraper
  - Unit tests for scheduler
  - Unit tests for coordinator
  - Pytest configuration
  - Test fixtures

## [Unreleased]

### Planned Features

- [ ] Calendar integration for viewing schedule
- [ ] Weather-based pre-heat adjustments
- [ ] Energy usage tracking
- [ ] Multi-zone support
- [ ] UI scraper configuration builder
- [ ] Scraper configuration import/export
- [ ] Historical heating data
- [ ] Mobile app notifications

## Version History

| Version | Date | Key Features |
|---------|------|--------------|
| 0.2.0 | 2024-11-26 | Configurable scraper, docs overhaul |
| 0.1.0 | 2024-11-24 | Initial release |

## Migration Guides

### Migrating from 0.1.0 to 0.2.0

**No breaking changes!** Your existing setup will continue to work.

**Optional: Switch to configurable scraper:**

1. Add `scraper_sources` to your configuration
2. Remove custom scraper Python files
3. See [[../scraper/configuring-scraper|Scraper Configuration Guide]]

**Example migration:**

Before (custom scraper):
```python
# Required editing Python code
self.scraper = ZHCCustomScraper(...)
```

After (configuration):
```yaml
# Just YAML configuration
scraper_sources:
  - url: "https://www.club.com/schedule"
    type: training
    selectors:
      container: "div.event"
      date: "span.date"
      time: "span.time"
```

## Support

- **Issues:** [GitHub Issues](https://github.com/stefan/zhc-heating-scheduler/issues)
- **Discussions:** [GitHub Discussions](https://github.com/stefan/zhc-heating-scheduler/discussions)
- **Forum:** [Home Assistant Community](https://community.home-assistant.io/)

---

[[../index|Back to Documentation Home]]

