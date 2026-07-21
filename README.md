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

On startup, ChronoBright reads the saved configuration (if any), immediately applies
whichever period — morning or evening — is currently active, and starts a background
daemon thread. The thread polls every second and detects **period transitions** (morning
↔ evening) rather than firing one-shot wall-clock jobs. This approach is
DST-safe: daylight-saving changes do not cause duplicate or skipped brightness updates.

Time inputs accept flexible formats (`8:0`, `9:5`) and are normalised to `HH:MM` before
validation and storage.

> **Multi-display note:** when a scheduled period applies, all detected displays are set to the same level. On exit, each display is restored to its own startup brightness level. Per-display schedules are not yet exposed in the UI; the underlying `BrightnessService.set_brightness(level, display=...)` API supports it for future use.

Closing the window sends the application to the system tray rather than quitting. From there you can show the window again or exit fully. On exit, each display is restored to the brightness it had when the application first launched.

## Configuration

User settings are stored at:

```
%APPDATA%\ChronoBright\config.json
```

The file is plain JSON and is written atomically every time you press **Save & Apply Schedule** (write to a temporary file, then replace). Times must use `HH:MM` format in the file; the UI accepts flexible input such as `8:0`. You can edit the file by hand if needed — the application validates it on load and falls back to defaults if something is wrong.

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
├── tests/                           # Unit and smoke tests
│   ├── conftest.py                  # Shared pytest fixtures
│   ├── test_app.py                  # Application logic (mocked GUI)
│   ├── test_app_smoke.py            # Import smoke test
│   ├── test_brightness_service.py
│   ├── test_config.py
│   ├── test_logger.py
│   ├── test_main.py
│   ├── test_models.py
│   ├── test_schedule_service.py
│   ├── test_settings_service.py
│   ├── test_theme.py
│   ├── test_time_utils.py
│   └── test_tray_service.py
├── .github/workflows/               # CI and release automation
│   ├── ci.yml                       # Lint, type-check, and test on Windows
│   └── release.yml                  # Build and publish release artifacts
└── chronobright/
    ├── __init__.py                  # Package version
    ├── __main__.py                  # Entry point (`python -m chronobright`)
    ├── config.py                    # App constants, paths, shared validators
    ├── logger.py                    # Centralised logging (lazy init)
    ├── models.py                    # Validated schedule data model
    ├── time_utils.py                # Time normalisation and period logic
    ├── services/
    │   ├── __init__.py
    │   ├── brightness_service.py    # Read/write display brightness
    │   ├── schedule_service.py      # Polling-based background scheduler
    │   ├── settings_service.py      # Atomic JSON config persistence
    │   └── tray_service.py          # System tray icon and menu
    └── ui/
        ├── __init__.py
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

Run tests with coverage (enforces an 85% threshold, configured in `pyproject.toml`; also checked in CI on Windows):

```bash
pytest --cov=chronobright --cov-report=term-missing
```

Pull requests and pushes to `main` trigger the GitHub Actions CI workflow (Windows runner: ruff, mypy, pytest with coverage). Tag pushes matching `v*` build release artifacts via `release.yml`.

## License

MIT
