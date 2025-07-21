# 🐚 Shelly CLI

A powerful command-line tool for organizing, managing, and working with multiple Git repositories. Shelly helps developers efficiently manage their codebase collections with intelligent categorization, bulk operations, and seamless integrations.

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/Domains18/shelly)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Features

### Current Features
- 🎯 **Smart Repository Cloning** - Clone repositories with automatic categorization
- 📁 **Category-based Organization** - Organize repos by work, personal, learning, etc.
- 🔍 **Repository Listing** - View all repositories grouped by category
- ⚙️ **Interactive Configuration** - Easy setup wizard for preferences
- 🚀 **Editor Integration** - Auto-open repositories in your preferred editor
- 📊 **Repository Caching** - Fast access to repository metadata

### Coming Soon
- 📈 **Git Status Dashboard** - View status of all repositories at once
- 🔄 **Bulk Git Operations** - Sync, pull, or check status across multiple repos
- 🏷️ **Project Type Detection** - Auto-detect React, Python, Rust, etc. projects
- 🌐 **GitHub/GitLab Integration** - Repository metadata, search, and CLI tool integration
- 🔧 **CI/CD Pipeline Awareness** - Show build status and deployment information
- 📦 **Package Manager Integration** - Dependency scanning and updates

## 🚀 Quick Start

### Installation

```bash
# Clone and install in development mode
git clone https://github.com/Domains18/shelly.git
cd shelly
pip install -e .
```

### Initial Setup

```bash
# Run the interactive setup wizard
shelly config --setup
```

This will configure:
- Base directory for repositories
- Organization method (category/platform/flat)
- Preferred editor
- Default categories

### Basic Usage

```bash
# Clone a repository (will prompt for category)
shelly clone https://github.com/facebook/react
# or use shorthand
shelly --clone https://github.com/facebook/react

# List all repositories
shelly list

# List repositories in specific category
shelly list --category work

# Open a repository in your editor
shelly open react

# View configuration
shelly config --list
```

## 📋 Commands

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `clone <url>` | Clone repository with category selection | `shelly clone https://github.com/user/repo` |
| `list` | List all managed repositories | `shelly list --category work` |
| `open <repo>` | Open repository in preferred editor | `shelly open my-project` |
| `config` | Manage configuration settings | `shelly config --setup` |
| `roadmap` | View development roadmap | `shelly roadmap --next` |

### Shorthand Options

| Option | Equivalent Command | Description |
|--------|-------------------|-------------|
| `--clone <url>` | `clone <url>` | Quick clone syntax |
| `--list` | `list` | Quick list repositories |
| `--config-setup` | `config --setup` | Quick setup configuration |

## 🏗️ Configuration

Shelly stores configuration in `~/.shelly/config.json`:

```json
{
  "auto_open_editor": true,
  "base_dir": "/home/user/Documents/github",
  "categories": [
    "work",
    "personal", 
    "learning",
    "opensource",
    "misc"
  ],
  "organization_method": "category",
  "preferred_editor": "vscode"
}
```

### Supported Editors

- Visual Studio Code (`vscode`)
- Cursor (`cursor`) 
- WebStorm (`webstorm`)
- IntelliJ IDEA (`intellij`)
- Sublime Text (`sublime`)
- Atom (`atom`)
- Vim/Neovim (`vim`/`nvim`)

## 🎯 Integration Roadmap

### Phase 1: Core Enhancements (Next 2-4 weeks)

#### Enhanced Git Operations
- **Repository Status Dashboard** - `shelly status --all`
  - Visual indicators for dirty repos, unpushed commits
  - Bulk status checking across categories
  - Git hooks integration for automatic cache updates

- **Bulk Git Operations** - `shelly git sync --category work`
  - Pull/sync all repositories in a category
  - Branch management helpers
  - Smart conflict resolution assistance

#### GitHub/GitLab Integration
- **Repository Metadata** - Auto-fetch stars, forks, issues count
- **Search and Clone** - `shelly clone search:react-router`
- **CLI Tool Integration** - Work with `gh` and `glab` commands
- **Repository Discovery** - Browse trending and user repositories

#### Smart Project Detection
- **Auto-detect Technologies** - Python, JavaScript, Rust, Go, etc.
- **Project-specific Commands** - Show relevant npm/cargo/pip commands
- **Environment Setup** - Auto-generate .gitignore, detect Docker
- **Development Shortcuts** - Quick access to build/test/run commands

### Phase 2: Advanced Features (1-2 months)

#### CI/CD Pipeline Awareness
- **Build Status Integration** - GitHub Actions, GitLab CI, Jenkins
- **Pipeline History** - View recent builds and deployments
- **Deployment Status** - Track production deployments
- **Configuration Detection** - Find and analyze CI/CD files

#### Package Manager Integration
- **Dependency Scanning** - Security vulnerabilities across all repos
- **Outdated Package Detection** - Find packages needing updates
- **Quick Updates** - Bulk dependency updates by category
- **Multi-language Support** - npm, pip, cargo, go mod, maven

#### Development Workflow Tools
- **Code Quality Metrics** - Health scores and technical debt
- **Test Integration** - Run tests across multiple repositories
- **Linting and Formatting** - Automated code style enforcement
- **Documentation** - Generate and maintain project documentation

### Phase 3: Enterprise Features (3+ months)

#### Cloud Platform Integration
- **Deployment Automation** - Deploy to Vercel, Netlify, Heroku, AWS
- **Environment Management** - Manage staging/production environments
- **Secret Management** - Secure handling of API keys and credentials
- **Resource Monitoring** - Track cloud resource usage and costs

#### Team Collaboration
- **Shared Collections** - Team-wide repository organization
- **Templates and Standards** - Enforce team coding standards
- **Code Review Helpers** - Streamline review workflows
- **Knowledge Sharing** - Documentation and onboarding tools

#### Advanced Analytics
- **Productivity Metrics** - Developer and team productivity insights
- **Technology Analysis** - Tech stack analysis and migration planning
- **Contribution Patterns** - Understand team collaboration patterns
- **Health Monitoring** - Repository and codebase health tracking

## 🔧 Development

### Project Structure

```
shelly/
├── setup.py                    # Package installation
├── requirements.txt           # Dependencies
├── README.md                 # Documentation
├── shelly/                   # Main package
│   ├── __init__.py          
│   ├── main.py              # CLI entry point
│   ├── commands/            # CLI commands
│   │   ├── clone.py         # Repository cloning
│   │   ├── config.py        # Configuration management
│   │   ├── list.py          # Repository listing
│   │   ├── open.py          # Editor integration
│   │   └── roadmap.py       # Development roadmap
│   ├── config/              # Configuration management
│   │   ├── manager.py       # Config file handling
│   │   └── settings.py      # Default settings
│   ├── core/                # Core functionality
│   │   ├── git_manager.py   # Git operations
│   │   ├── repository.py    # Repository management
│   │   └── utils.py         # Utility functions
│   └── ui/                  # User interface
│       ├── display.py       # Output formatting
│       └── prompts.py       # Interactive prompts
└── tests/                   # Test files
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=shelly tests/
```

## 📝 Usage Examples

### Organizing Work Projects

```bash
# Setup work category
shelly config --setup

# Clone work repositories
shelly clone https://github.com/company/backend-api
shelly clone https://github.com/company/frontend-app
shelly clone https://github.com/company/mobile-app

# List work projects
shelly list --category work

# Open entire work environment
shelly open backend-api
```

### Learning and Experimentation

```bash
# Clone learning resources
shelly --clone https://github.com/microsoft/TypeScript
shelly --clone https://github.com/rust-lang/book

# Quick access to learning materials
shelly list --category learning
shelly open TypeScript
```

### Contributing to Open Source

```bash
# Clone and categorize open source projects
shelly clone https://github.com/facebook/react
# Select "opensource" category

# Track your contributions
shelly list --category opensource
```

## 🆘 Support

- 📖 [Documentation](https://github.com/Domains18/shelly/wiki)
- 🐛 [Bug Reports](https://github.com/Domains18/shelly/issues)
- 💡 [Feature Requests](https://github.com/Domains18/shelly/issues)
- 💬 [Discussions](https://github.com/Domains18/shelly/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for better repository management in modern development workflows
- Built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
- Special thanks to the open source community for inspiration and feedback

---

**Made with ❤️ for developers who manage multiple repositories**
