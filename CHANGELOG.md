# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-24

### Added
- Initial release
- HTML schedule scraping with flexible parser
- Heating schedule calculation with pre-heat and cool-down times
- Automatic climate device control (Plugwise SA support)
- UI configuration flow
- YAML configuration support
- Multiple sensors for schedule information:
  - Next heating start/stop times
  - Current event details
  - Events today count
  - Heating minutes today
  - Total heating windows
  - Last schedule update
- Binary sensors:
  - Heating active status
  - Scheduler enabled status
  - Manual override status
- Services:
  - Refresh schedule
  - Enable/disable scheduler
  - Set/clear manual override
- Dry run mode for testing
- Manual override capability
- Comprehensive documentation
- Unit and integration tests

### Known Issues
- Generic HTML parser may not work with all websites (customization may be needed)
- No support for multiple climate zones in a single integration instance

## [Unreleased]

### Planned Features
- Calendar integration for viewing heating schedule
- Weather-based adjustments to pre-heat times
- Energy usage tracking
- Multiple zone support
- Integration with other event sources (Google Calendar, iCal, etc.)
- Historical heating data and statistics
- Mobile app notifications
- HACS integration

