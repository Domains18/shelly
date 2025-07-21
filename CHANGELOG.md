# Changelog

All notable changes to Shelly CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Enhanced Git Status Dashboard (`shelly status --all`)
- Bulk Git Operations (`shelly git sync --category work`)
- GitHub/GitLab API Integration
- Project Type Detection
- CI/CD Pipeline Awareness
- Package Manager Integration

## [0.1.0] - 2025-07-22

### Added
- Initial release of Shelly CLI
- Repository cloning with category organization (`shelly clone <url>`)
- Interactive category selection during clone
- Shorthand clone syntax (`shelly --clone <url>`)
- Repository listing by category (`shelly list`)
- Configuration management with interactive setup (`shelly config --setup`)
- Editor integration with auto-open functionality
- Support for multiple editors (VS Code, Cursor, WebStorm, IntelliJ, etc.)
- Repository caching for fast access
- Development roadmap command (`shelly roadmap`)
- Click-based CLI framework
- Rich terminal output formatting
- Comprehensive project structure and documentation

### Project Structure
- Core CLI functionality in `shelly/main.py`
- Modular command system in `shelly/commands/`
- Configuration management in `shelly/config/`
- Git operations foundation in `shelly/core/`
- User interface helpers in `shelly/ui/`
- Complete test structure in `tests/`

### Configuration Features
- JSON-based configuration storage (`~/.shelly/config.json`)
- Repository cache system (`~/.shelly/cache.json`)
- Customizable base directories
- Category management
- Editor preferences
- Organization methods (category/platform/flat)

### Commands Implemented
- `shelly clone <url>` - Clone repository with category selection
- `shelly list [--category <cat>] [--recent] [--path]` - List repositories
- `shelly open <repo> [--editor <editor>]` - Open repository in editor
- `shelly config [--setup] [--list] [--set key value]` - Configuration management
- `shelly roadmap [--phase <1|2|3>] [--next]` - View development roadmap

### Shorthand Options
- `shelly --clone <url>` - Quick clone
- `shelly --list` - Quick list
- `shelly --config-setup` - Quick setup

### Technical Foundation
- Python 3.8+ support
- Click framework for CLI
- Rich library for formatted output
- GitPython for Git operations
- PyYAML for configuration
- Comprehensive error handling
- Development mode installation support

### Documentation
- Comprehensive README with usage examples
- Integration roadmap with 3-phase development plan
- Project structure documentation
- Contributing guidelines
- Installation and setup instructions
