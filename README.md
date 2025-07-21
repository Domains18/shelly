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
- 📈 **Git Status Dashboard** - View status of all repositories at once
- 🔄 **Bulk Git Operations** - Sync, pull, or check status across multiple repos
- 🏗️ **Project Initialization** - Create new projects with opinionated structures

### Coming Soon
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

# Initialize a new project
shelly init my-api --language typescript --framework nestjs --orm prisma
# or use shorthand
shelly --init my-project

# List all repositories
shelly list

# List repositories in specific category
shelly list --category work

# Git operations across repositories
shelly git sync --category work
shelly status --detailed

# Open a repository in your editor
shelly open react

# View configuration
shelly config --list
```

## 🏗️ Project Initialization

Shelly can create new projects with opinionated directory structures and configurations for various languages and frameworks.

### Supported Languages & Frameworks

| Language | Frameworks | ORMs/Databases |
|----------|------------|----------------|
| **TypeScript** | NestJS, Express, Fastify, Koa | Prisma, TypeORM, Sequelize, Mongoose, Drizzle |
| **JavaScript** | Express, Fastify, Koa, React, Vue, Svelte | Prisma, Sequelize, Mongoose, Knex |
| **Python** | FastAPI, Django, Flask, Quart | SQLAlchemy, Django ORM, Tortoise ORM, Peewee |
| **Go** | Gin, Echo, Fiber, Chi | GORM, Ent, SQLX |
| **Rust** | Axum, Warp, Actix-web, Rocket | Diesel, SQLX, Sea-ORM |
| **Java** | Spring Boot, Quarkus, Micronaut | JPA, Hibernate, MyBatis |

### Project Types
- **API** - REST API with controllers, services, and models
- **Microservice** - Microservice with event handling and DTOs
- **Monolith** - Monolithic application structure
- **GraphQL** - GraphQL API setup
- **CLI** - Command line tool structure
- **Library** - Library/package template
- **Web App** - Full-stack web application

### Examples

```bash
# Interactive mode
shelly init my-project

# TypeScript NestJS API with Prisma
shelly init backend-api --language typescript --framework nestjs --orm prisma --type api

# Go microservice with Gin and GORM
shelly init user-service --language go --framework gin --orm gorm --type microservice

# Python FastAPI with SQLAlchemy
shelly init data-api --language python --framework fastapi --orm sqlalchemy --type api

# Shorthand syntax
shelly --init my-new-project
```

### What Gets Created

For a **TypeScript NestJS API**, Shelly creates:

```
my-api/
├── src/
│   ├── modules/         # Feature modules
│   ├── common/          # Shared utilities
│   │   ├── decorators/
│   │   ├── filters/
│   │   ├── guards/
│   │   ├── interceptors/
│   │   └── pipes/
│   ├── config/          # Configuration
│   ├── controllers/     # API controllers
│   ├── services/        # Business logic
│   ├── entities/        # Database entities
│   └── repositories/    # Data access layer
├── test/                # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── prisma/              # Database schema (if Prisma selected)
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

## 📋 Commands

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `clone <url>` | Clone repository with category selection | `shelly clone https://github.com/user/repo` |
| `init <name>` | Initialize new project with opinionated structure | `shelly init my-api --language typescript --framework nestjs` |
| `list` | List all managed repositories | `shelly list --category work` |
| `open <repo>` | Open repository in preferred editor | `shelly open my-project` |
| `config` | Manage configuration settings | `shelly config --setup` |
| `status` | Show git status across repositories | `shelly status --detailed` |
| `git sync` | Synchronize repositories with remotes | `shelly git sync --category work` |
| `roadmap` | View development roadmap | `shelly roadmap --next` |

### Shorthand Options

| Option | Equivalent Command | Description |
|--------|-------------------|-------------|
| `--clone <url>` | `clone <url>` | Quick clone syntax |
| `--init <name>` | `init <name>` | Quick project initialization |
| `--list` | `list` | Quick list repositories |
| `--status` | `status` | Quick status check |
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
