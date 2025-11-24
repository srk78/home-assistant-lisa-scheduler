# Development Guide

This guide helps you set up a development environment for the ZHC Heating Scheduler integration.

## Prerequisites

- Python 3.11 or newer
- Home Assistant (for testing)
- Git
- Basic knowledge of Python and Home Assistant development

## Setting Up Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/stefan/zhc-heating-scheduler.git
cd zhc-heating-scheduler
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements_dev.txt
```

If `requirements_dev.txt` doesn't exist, create it:

```txt
homeassistant>=2024.1.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-homeassistant-custom-component>=0.13.0
beautifulsoup4==4.12.2
aiohttp==3.9.1
python-dateutil==2.8.2
```

### 4. Install Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

## Project Structure

```
zhc-heating-scheduler/
├── custom_components/
│   └── zhc_heating_scheduler/
│       ├── __init__.py           # Integration setup
│       ├── binary_sensor.py      # Binary sensor platform
│       ├── config_flow.py        # UI configuration
│       ├── const.py              # Constants
│       ├── coordinator.py        # Data coordinator
│       ├── manifest.json         # Integration metadata
│       ├── scheduler.py          # Heating schedule logic
│       ├── scraper.py            # HTML scraper
│       ├── sensor.py             # Sensor platform
│       ├── services.yaml         # Service definitions
│       └── translations/
│           └── en.json           # English translations
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   ├── test_coordinator.py      # Coordinator tests
│   ├── test_scheduler.py        # Scheduler tests
│   └── test_scraper.py          # Scraper tests
├── .gitignore
├── LICENSE
├── README.md
├── CONFIGURATION.md
├── DEVELOPMENT.md
├── SCRAPER_GUIDE.md
└── pytest.ini
```

## Running Tests

### All Tests

```bash
pytest
```

### Specific Test File

```bash
pytest tests/test_scheduler.py
```

### With Coverage

```bash
pytest --cov=custom_components.zhc_heating_scheduler --cov-report=html
```

### Verbose Output

```bash
pytest -v
```

## Code Style

### Formatting with Black

```bash
black custom_components/zhc_heating_scheduler
```

### Linting with Flake8

```bash
flake8 custom_components/zhc_heating_scheduler
```

### Type Checking with mypy

```bash
mypy custom_components/zhc_heating_scheduler
```

## Testing in Home Assistant

### Method 1: Symbolic Link (Development)

1. Find your Home Assistant config directory (usually `~/.homeassistant`)
2. Create a symbolic link:

```bash
ln -s /path/to/zhc-heating-scheduler/custom_components/zhc_heating_scheduler \
      ~/.homeassistant/custom_components/zhc_heating_scheduler
```

3. Restart Home Assistant

### Method 2: Copy Files (Testing)

```bash
cp -r custom_components/zhc_heating_scheduler ~/.homeassistant/custom_components/
```

### Enable Debug Logging

In `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.zhc_heating_scheduler: debug
```

## Development Workflow

### Adding a New Feature

1. Create a new branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. Make your changes

3. Add tests for your changes

4. Run tests:
   ```bash
   pytest
   ```

5. Check code style:
   ```bash
   black custom_components/zhc_heating_scheduler
   flake8 custom_components/zhc_heating_scheduler
   ```

6. Commit your changes:
   ```bash
   git add .
   git commit -m "Add my new feature"
   ```

7. Push and create a pull request:
   ```bash
   git push origin feature/my-new-feature
   ```

### Fixing a Bug

1. Create an issue describing the bug
2. Create a branch:
   ```bash
   git checkout -b fix/issue-123
   ```
3. Fix the bug and add a test that reproduces it
4. Follow the same process as adding a feature

## Architecture Overview

### Data Flow

```
Website (HTML)
    ↓
Scraper (scraper.py)
    ↓
Events List
    ↓
Scheduler (scheduler.py)
    ↓
Heating Windows
    ↓
Coordinator (coordinator.py)
    ↓
Climate Device Control + Sensors
```

### Key Components

#### Scraper (`scraper.py`)
- Fetches HTML from website
- Parses events from HTML
- Returns list of Event objects
- Can be customized for specific websites

#### Scheduler (`scheduler.py`)
- Takes events and configuration
- Calculates heating windows (start/stop times)
- Merges overlapping windows
- Determines current heating state

#### Coordinator (`coordinator.py`)
- Orchestrates scraper and scheduler
- Controls the climate device
- Provides data to sensors
- Handles manual overrides
- Manages update intervals

#### Config Flow (`config_flow.py`)
- Handles UI configuration
- Validates user input
- Creates/updates config entries

#### Sensors (`sensor.py`, `binary_sensor.py`)
- Expose schedule information
- Update when coordinator data changes

## Adding a New Sensor

1. Add sensor to `sensor.py` or `binary_sensor.py`:

```python
class MyNewSensor(ZHCSchedulerSensorBase):
    """Description of sensor."""
    
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "my_sensor", "My Sensor")
        self._attr_icon = "mdi:icon-name"
    
    @property
    def native_value(self):
        """Return sensor value."""
        return self.coordinator.data.get("some_value")
```

2. Add to sensor list in `async_setup_entry`:

```python
sensors = [
    # ... existing sensors
    MyNewSensor(coordinator, config_entry),
]
```

3. Add translation to `translations/en.json`

4. Add test in `tests/test_sensor.py`

## Adding a New Service

1. Add service constant to `const.py`:

```python
SERVICE_MY_SERVICE = "my_service"
```

2. Add service handler in `__init__.py`:

```python
async def handle_my_service(call: ServiceCall) -> None:
    """Handle my service."""
    # Implementation
    pass

hass.services.async_register(DOMAIN, SERVICE_MY_SERVICE, handle_my_service)
```

3. Add service definition to `services.yaml`:

```yaml
my_service:
  name: My Service
  description: Description of what it does.
  fields:
    my_field:
      name: My Field
      description: Description of field.
      required: true
      example: "example value"
```

4. Add translation to `translations/en.json`

5. Add test in `tests/test_services.py`

## Debugging Tips

### Print Debugging

Use the logger instead of print:

```python
_LOGGER.debug("Debug message")
_LOGGER.info("Info message")
_LOGGER.warning("Warning message")
_LOGGER.error("Error message")
```

### Interactive Debugging

Use pdb:

```python
import pdb; pdb.set_trace()
```

Or use VS Code debugger with this launch configuration:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Home Assistant",
            "type": "python",
            "request": "launch",
            "module": "homeassistant",
            "args": [
                "-c",
                "/path/to/config",
                "--debug"
            ]
        }
    ]
}
```

### Testing Scraper

Test scraper independently:

```python
import asyncio
from custom_components.zhc_heating_scheduler.scraper import ScheduleScraper

async def test():
    async with ScheduleScraper("http://example.com") as scraper:
        events = await scraper.fetch_schedule()
        print(f"Found {len(events)} events")
        for event in events:
            print(event)

asyncio.run(test())
```

## Common Issues

### Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

### Tests Failing

Check that all dependencies are installed:
```bash
pip install -r requirements_dev.txt
```

### Integration Not Loading

Check Home Assistant logs:
```bash
tail -f /path/to/config/home-assistant.log
```

## Release Process

1. Update version in `manifest.json`
2. Update CHANGELOG.md
3. Run all tests
4. Create a git tag:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```
5. Create a GitHub release
6. Submit to HACS (if applicable)

## Contributing

### Guidelines

- Follow Home Assistant coding standards
- Write tests for new features
- Update documentation
- Use meaningful commit messages
- Keep pull requests focused

### Commit Message Format

```
type: brief description

Longer description if needed

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Home Assistant Architecture](https://developers.home-assistant.io/docs/architecture_index)
- [Integration Development](https://developers.home-assistant.io/docs/creating_integration_manifest)
- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)

## Getting Help

- GitHub Issues: Report bugs or request features
- GitHub Discussions: Ask questions
- Home Assistant Community: General help
- Discord: Real-time chat

## License

This project is licensed under the MIT License - see LICENSE file for details.

