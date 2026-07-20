# ChronoBright

ChronoBright is a lightweight Windows desktop application that automatically adjusts your display brightness on a schedule. You set a morning level and an evening level, each with its own time, and ChronoBright handles the rest in the background from the system tray.

## Requirements

- Windows 10 or 11
- Python 3.11 or later
- A display that supports software brightness control (most laptop screens; some external monitors via DDC/CI)

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/ulaskizilay/ChronoBright.git
cd ChronoBright
pip install -r requirements.txt
```

To install as a local package so you can run it with the `chronobright` command:

```bash
pip install -e .
```

## Running

If installed as a package:

```bash
chronobright
```

Or as a module from the repository root:

```bash
python -m chronobright
```

## How It Works

On startup, ChronoBright reads the saved configuration (if any), immediately sets brightness to whichever period — morning or evening — is currently active, and registers two daily jobs with the scheduler. A daemon thread ticks the scheduler every second in the background, so you never have to think about it.

> **Multi-display note:** when a scheduled period applies, all detected displays are set to the same level. On exit, each display is restored to its own startup level. Per-display schedules are not yet exposed in the UI; the underlying `BrightnessService.set_brightness(level, display=...)` API supports it for future use.

Closing the window sends the application to the system tray rather than quitting. From there you can show the window again or exit fully. On exit, the display is restored to the brightness it had when the application first launched.

## Configuration

User settings are stored at:

```
%APPDATA%\ChronoBright\config.json
```

The file is plain JSON and is written every time you press **Save & Apply Schedule**. You can edit it by hand if needed — the application validates it on load and falls back to defaults if something is wrong.

## Logs

Application logs are written to:

```
%APPDATA%\ChronoBright\logs\chronobright.log
```

Log output also appears in the console when the application is started from a terminal.

## Project Structure

```
ChronoBright/
├── pyproject.toml                   # Package metadata and build config
├── requirements.txt                 # Pinned production dependencies
├── requirements-dev.txt             # Development tools (ruff, mypy, pytest)
└── chronobright/
    ├── __init__.py                  # Package version
    ├── __main__.py                  # Entry point (`python -m chronobright`)
    ├── config.py                    # App constants, platform-aware paths, shared validators
    ├── logger.py                    # Centralised logging configuration
    ├── models.py                    # Validated schedule data model
    ├── services/
    │   ├── brightness_service.py    # Read/write display brightness
    │   ├── schedule_service.py      # Background scheduler thread
    │   ├── settings_service.py      # Config persistence (JSON)
    │   └── tray_service.py          # System tray icon and menu
    └── ui/
        ├── app.py                   # Main application window
        └── theme.py                 # CustomTkinter theme setup
```

## Development

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Lint and type-check:

```bash
ruff check .
mypy chronobright
```

Run tests:

```bash
pytest
```

Run tests with coverage (enforces an 85% threshold, configured in `pyproject.toml`):

```bash
pytest --cov=chronobright --cov-report=term-missing
```

## License

MIT
