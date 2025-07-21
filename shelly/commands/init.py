"""
Project initialization command
Creates new projects with opinionated directory structures and configurations
"""

import click
import os
import json
from pathlib import Path
import subprocess
from typing import Dict, List, Optional
from .base import BaseCommand
from ..ui.display import print_success, print_error, print_info, print_warning
from ..ui.prompts import select_from_list, confirm_action


# Supported languages and frameworks
LANGUAGES = {
    'typescript': {
        'name': 'TypeScript',
        'frameworks': ['nestjs', 'express', 'fastify', 'koa'],
        'extensions': ['.ts', '.js'],
        'gitignore': 'Node'
    },
    'javascript': {
        'name': 'JavaScript',
        'frameworks': ['express', 'fastify', 'koa', 'react', 'vue', 'svelte'],
        'extensions': ['.js', '.mjs'],
        'gitignore': 'Node'
    },
    'python': {
        'name': 'Python',
        'frameworks': ['fastapi', 'django', 'flask', 'quart'],
        'extensions': ['.py'],
        'gitignore': 'Python'
    },
    'go': {
        'name': 'Go',
        'frameworks': ['gin', 'echo', 'fiber', 'chi'],
        'extensions': ['.go'],
        'gitignore': 'Go'
    },
    'rust': {
        'name': 'Rust',
        'frameworks': ['axum', 'warp', 'actix-web', 'rocket'],
        'extensions': ['.rs'],
        'gitignore': 'Rust'
    },
    'java': {
        'name': 'Java',
        'frameworks': ['spring-boot', 'quarkus', 'micronaut'],
        'extensions': ['.java'],
        'gitignore': 'Java'
    }
}

# ORM/Database options
ORMS = {
    'typescript': ['prisma', 'typeorm', 'sequelize', 'mongoose', 'drizzle'],
    'javascript': ['prisma', 'sequelize', 'mongoose', 'knex'],
    'python': ['sqlalchemy', 'django-orm', 'tortoise-orm', 'peewee'],
    'go': ['gorm', 'ent', 'sqlx'],
    'rust': ['diesel', 'sqlx', 'sea-orm'],
    'java': ['jpa', 'hibernate', 'mybatis']
}

# Project types
PROJECT_TYPES = {
    'api': 'REST API',
    'microservice': 'Microservice',
    'monolith': 'Monolithic Application',
    'graphql': 'GraphQL API',
    'cli': 'Command Line Tool',
    'library': 'Library/Package',
    'webapp': 'Web Application'
}


@click.command()
@click.argument('name', required=False)
@click.option('--language', '-l', help='Programming language (typescript, python, go, etc.)')
@click.option('--framework', '-f', help='Framework to use')
@click.option('--orm', help='ORM/Database library to use')
@click.option('--type', 'project_type', help='Project type (api, microservice, etc.)')
@click.option('--git/--no-git', default=True, help='Initialize git repository')
@click.option('--category', '-c', help='Category for the project')
@click.option('--dir', 'custom_dir', help='Custom directory to create project in')
def init(name, language, framework, orm, project_type, git, category, custom_dir):
    """Initialize a new project with opinionated structure and configurations.
    
    Examples:
      shelly init my-api --language typescript --framework nestjs --orm prisma
      shelly init microservice --type microservice --language go --framework gin
      shelly --init my-project  # Interactive mode
    """
    base_cmd = BaseCommand()
    config = base_cmd.config
    
    # Get project name if not provided
    if not name:
        name = click.prompt('Project name', type=str)
    
    # Validate project name
    if not is_valid_project_name(name):
        print_error("Invalid project name. Use only letters, numbers, hyphens, and underscores.")
        return
    
    # Interactive prompts for missing options
    if not language:
        language = select_from_list(
            "Select programming language:",
            list(LANGUAGES.keys()),
            display_func=lambda x: LANGUAGES[x]['name']
        )
    
    if language not in LANGUAGES:
        print_error(f"Unsupported language: {language}")
        return
    
    if not framework:
        frameworks = LANGUAGES[language]['frameworks']
        if frameworks:
            framework = select_from_list(
                f"Select {LANGUAGES[language]['name']} framework:",
                frameworks
            )
    
    if not project_type:
        project_type = select_from_list(
            "Select project type:",
            list(PROJECT_TYPES.keys()),
            display_func=lambda x: PROJECT_TYPES[x]
        )
    
    if not orm and language in ORMS and project_type in ['api', 'microservice', 'monolith', 'webapp']:
        orm_options = ORMS[language]
        if orm_options:
            orm = select_from_list(
                f"Select ORM/Database library (or skip):",
                ['none'] + orm_options
            )
            if orm == 'none':
                orm = None
    
    if not category:
        categories = config.config.get('categories', ['work', 'personal', 'learning', 'opensource'])
        category = select_from_list(
            "Select project category:",
            categories + ['new category']
        )
        if category == 'new category':
            category = click.prompt('Enter new category name', type=str)
    
    # Determine project directory
    if custom_dir:
        project_dir = Path(custom_dir) / name
    else:
        base_dir = Path(config.config.get('base_dir', Path.home() / 'Documents' / 'github'))
        if config.config.get('organization_method') == 'category':
            project_dir = base_dir / category / name
        else:
            project_dir = base_dir / name
    
    # Check if directory already exists
    if project_dir.exists():
        if not confirm_action(f"Directory {project_dir} already exists. Continue?"):
            return
    
    # Create project
    print_info(f"🚀 Creating {LANGUAGES[language]['name']} {PROJECT_TYPES[project_type]} project...")
    print_info(f"📁 Location: {project_dir}")
    
    try:
        # Create directory structure
        create_project_structure(project_dir, language, framework, orm, project_type)
        
        # Create common files
        create_common_files(project_dir, name, language, framework, orm, project_type)
        
        # Initialize git if requested
        if git:
            init_git_repo(project_dir, language)
        
        # Add to shelly cache
        add_to_cache(config, name, project_dir, category, language, framework)
        
        print_success(f"✅ Project '{name}' created successfully!")
        print_info(f"📍 Location: {project_dir}")
        
        # Show next steps
        show_next_steps(name, project_dir, language, framework, orm)
        
    except Exception as e:
        print_error(f"Failed to create project: {str(e)}")


def is_valid_project_name(name: str) -> bool:
    """Validate project name."""
    import re
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))


def create_project_structure(project_dir: Path, language: str, framework: str, orm: str, project_type: str):
    """Create the directory structure based on language and framework."""
    project_dir.mkdir(parents=True, exist_ok=True)
    
    if language == 'typescript' and framework == 'nestjs':
        create_nestjs_structure(project_dir, project_type, orm)
    elif language == 'typescript' and framework == 'express':
        create_express_structure(project_dir, project_type, orm)
    elif language == 'python' and framework == 'fastapi':
        create_fastapi_structure(project_dir, project_type, orm)
    elif language == 'python' and framework == 'django':
        create_django_structure(project_dir, project_type, orm)
    elif language == 'go':
        create_go_structure(project_dir, framework, project_type)
    elif language == 'rust':
        create_rust_structure(project_dir, framework, project_type)
    else:
        create_generic_structure(project_dir, language, project_type)


def create_nestjs_structure(project_dir: Path, project_type: str, orm: str):
    """Create NestJS project structure."""
    dirs = [
        'src',
        'src/modules',
        'src/common',
        'src/common/decorators',
        'src/common/filters',
        'src/common/guards',
        'src/common/interceptors',
        'src/common/pipes',
        'src/config',
        'test',
        'test/unit',
        'test/integration',
        'test/e2e'
    ]
    
    if project_type == 'microservice':
        dirs.extend([
            'src/events',
            'src/dto',
            'src/interfaces'
        ])
    
    if project_type in ['api', 'microservice', 'monolith']:
        dirs.extend([
            'src/controllers',
            'src/services',
            'src/entities',
            'src/repositories'
        ])
    
    if orm == 'prisma':
        dirs.append('prisma')
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)


def create_express_structure(project_dir: Path, project_type: str, orm: str):
    """Create Express.js project structure."""
    dirs = [
        'src',
        'src/routes',
        'src/middleware',
        'src/controllers',
        'src/services',
        'src/models',
        'src/utils',
        'src/config',
        'tests',
        'public'
    ]
    
    if project_type == 'microservice':
        dirs.extend([
            'src/events',
            'src/dto'
        ])
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)


def create_fastapi_structure(project_dir: Path, project_type: str, orm: str):
    """Create FastAPI project structure."""
    dirs = [
        'app',
        'app/api',
        'app/api/v1',
        'app/core',
        'app/models',
        'app/schemas',
        'app/services',
        'app/utils',
        'tests',
        'tests/unit',
        'tests/integration'
    ]
    
    if project_type == 'microservice':
        dirs.extend([
            'app/events',
            'app/handlers'
        ])
    
    if orm == 'sqlalchemy':
        dirs.extend([
            'app/database',
            'alembic'
        ])
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)


def create_django_structure(project_dir: Path, project_type: str, orm: str):
    """Create Django project structure."""
    dirs = [
        'project',
        'apps',
        'static',
        'media',
        'templates',
        'requirements',
        'docs'
    ]
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)


def create_go_structure(project_dir: Path, framework: str, project_type: str):
    """Create Go project structure."""
    dirs = [
        'cmd',
        'internal',
        'internal/handler',
        'internal/service',
        'internal/repository',
        'internal/model',
        'internal/config',
        'pkg',
        'api',
        'docs',
        'scripts',
        'test'
    ]
    
    if project_type == 'microservice':
        dirs.extend([
            'internal/event',
            'internal/proto'
        ])
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)


def create_rust_structure(project_dir: Path, framework: str, project_type: str):
    """Create Rust project structure."""
    dirs = [
        'src',
        'src/handlers',
        'src/services',
        'src/models',
        'src/config',
        'tests',
        'docs'
    ]
    
    if project_type == 'microservice':
        dirs.extend([
            'src/events',
            'src/proto'
        ])
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)


def create_generic_structure(project_dir: Path, language: str, project_type: str):
    """Create generic project structure."""
    dirs = [
        'src',
        'tests',
        'docs'
    ]
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)


def create_common_files(project_dir: Path, name: str, language: str, framework: str, orm: str, project_type: str):
    """Create common configuration and template files."""
    
    # Create README.md
    create_readme(project_dir, name, language, framework, orm, project_type)
    
    # Create .gitignore
    create_gitignore(project_dir, language)
    
    # Create language-specific files
    if language in ['typescript', 'javascript']:
        create_nodejs_files(project_dir, name, framework, orm, project_type)
    elif language == 'python':
        create_python_files(project_dir, name, framework, orm, project_type)
    elif language == 'go':
        create_go_files(project_dir, name, framework, project_type)
    elif language == 'rust':
        create_rust_files(project_dir, name, framework, project_type)


def create_readme(project_dir: Path, name: str, language: str, framework: str, orm: str, project_type: str):
    """Create README.md file."""
    content = f"""# {name.title()}

{PROJECT_TYPES.get(project_type, 'Application')} built with {LANGUAGES[language]['name']}"""
    
    if framework:
        content += f" and {framework.title()}"
    
    content += f"""

## Description

TODO: Add project description

## Tech Stack

- **Language**: {LANGUAGES[language]['name']}"""
    
    if framework:
        content += f"\n- **Framework**: {framework.title()}"
    
    if orm:
        content += f"\n- **ORM/Database**: {orm.title()}"
    
    content += """

## Getting Started

### Prerequisites

TODO: List prerequisites

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd """ + name + """

# Install dependencies
# TODO: Add installation commands
```

### Running the Application

```bash
# TODO: Add run commands
```

## Development

### Project Structure

```
""" + name + """/
├── src/                 # Source code
├── tests/              # Test files
├── docs/               # Documentation
└── README.md           # This file
```

### Testing

```bash
# TODO: Add test commands
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

TODO: Add license information
"""
    
    (project_dir / 'README.md').write_text(content)


def create_gitignore(project_dir: Path, language: str):
    """Create .gitignore file."""
    gitignore_templates = {
        'Node': """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
dist/
build/
.next/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
""",
        'Python': """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
env/
.venv/
.env/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# Testing
.coverage
htmlcov/
.pytest_cache/
""",
        'Go': """# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib

# Go workspace file
go.work

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
coverage.out
""",
        'Rust': """# Generated files
target/
Cargo.lock

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
""",
        'Java': """# Compiled class file
*.class

# Log file
*.log

# Package Files
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# Virtual machine crash logs
hs_err_pid*

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Maven
target/

# Gradle
.gradle/
build/
"""
    }
    
    gitignore_type = LANGUAGES[language]['gitignore']
    content = gitignore_templates.get(gitignore_type, "# Add your gitignore rules here\n")
    
    (project_dir / '.gitignore').write_text(content)


def create_nodejs_files(project_dir: Path, name: str, framework: str, orm: str, project_type: str):
    """Create Node.js specific files."""
    
    # package.json
    package_json = {
        "name": name,
        "version": "1.0.0",
        "description": "",
        "main": "dist/index.js",
        "scripts": {
            "build": "tsc",
            "start": "node dist/index.js",
            "dev": "ts-node-dev --respawn --transpile-only src/index.ts",
            "test": "jest"
        },
        "keywords": [],
        "author": "",
        "license": "MIT",
        "devDependencies": {
            "@types/node": "^20.0.0",
            "typescript": "^5.0.0",
            "ts-node-dev": "^2.0.0",
            "jest": "^29.0.0",
            "@types/jest": "^29.0.0"
        },
        "dependencies": {}
    }
    
    if framework == 'nestjs':
        package_json["scripts"].update({
            "start": "nest start",
            "start:dev": "nest start --watch",
            "start:debug": "nest start --debug --watch",
            "start:prod": "node dist/main",
            "build": "nest build",
            "test": "jest",
            "test:watch": "jest --watch",
            "test:cov": "jest --coverage",
            "test:debug": "node --inspect-brk -r tsconfig-paths/register -r ts-node/register node_modules/.bin/jest --runInBand",
            "test:e2e": "jest --config ./test/jest-e2e.json"
        })
        package_json["dependencies"].update({
            "@nestjs/common": "^10.0.0",
            "@nestjs/core": "^10.0.0",
            "@nestjs/platform-express": "^10.0.0",
            "reflect-metadata": "^0.1.13",
            "rxjs": "^7.0.0"
        })
    elif framework == 'express':
        package_json["dependencies"].update({
            "express": "^4.18.0",
            "@types/express": "^4.17.0"
        })
    
    if orm == 'prisma':
        package_json["dependencies"]["@prisma/client"] = "^5.0.0"
        package_json["devDependencies"]["prisma"] = "^5.0.0"
    
    (project_dir / 'package.json').write_text(json.dumps(package_json, indent=2))
    
    # tsconfig.json
    if framework == 'nestjs':
        tsconfig = {
            "compilerOptions": {
                "module": "commonjs",
                "declaration": True,
                "removeComments": True,
                "emitDecoratorMetadata": True,
                "experimentalDecorators": True,
                "allowSyntheticDefaultImports": True,
                "target": "ES2020",
                "sourceMap": True,
                "outDir": "./dist",
                "baseUrl": "./",
                "incremental": True,
                "skipLibCheck": True,
                "strictNullChecks": False,
                "noImplicitAny": False,
                "strictBindCallApply": False,
                "forceConsistentCasingInFileNames": False,
                "noFallthroughCasesInSwitch": False
            }
        }
    else:
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }
    
    (project_dir / 'tsconfig.json').write_text(json.dumps(tsconfig, indent=2))


def create_python_files(project_dir: Path, name: str, framework: str, orm: str, project_type: str):
    """Create Python specific files."""
    
    # requirements.txt
    requirements = []
    
    if framework == 'fastapi':
        requirements.extend(['fastapi', 'uvicorn[standard]'])
    elif framework == 'django':
        requirements.append('django')
    elif framework == 'flask':
        requirements.append('flask')
    
    if orm == 'sqlalchemy':
        requirements.append('sqlalchemy')
    elif orm == 'django-orm' and framework == 'django':
        pass  # Already included with Django
    
    requirements.extend(['python-dotenv', 'pytest'])
    
    (project_dir / 'requirements.txt').write_text('\n'.join(requirements) + '\n')
    
    # pyproject.toml
    pyproject = f"""[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = ""
authors = [{{name = "Your Name", email = "your.email@example.com"}}]
license = {{text = "MIT"}}
requires-python = ">=3.8"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "black", "flake8", "mypy"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
"""
    
    (project_dir / 'pyproject.toml').write_text(pyproject)


def create_go_files(project_dir: Path, name: str, framework: str, project_type: str):
    """Create Go specific files."""
    
    # go.mod
    go_mod = f"""module {name}

go 1.21

require (
)
"""
    
    (project_dir / 'go.mod').write_text(go_mod)
    
    # main.go
    main_go = f"""package main

import (
    "fmt"
)

func main() {{
    fmt.Println("Hello from {name}!")
}}
"""
    
    (project_dir / 'cmd' / 'main.go').write_text(main_go)


def create_rust_files(project_dir: Path, name: str, framework: str, project_type: str):
    """Create Rust specific files."""
    
    # Cargo.toml
    cargo_toml = f"""[package]
name = "{name}"
version = "0.1.0"
edition = "2021"

[dependencies]
"""
    
    if framework == 'axum':
        cargo_toml += """axum = "0.7"
tokio = { version = "1.0", features = ["full"] }
"""
    
    (project_dir / 'Cargo.toml').write_text(cargo_toml)
    
    # main.rs
    main_rs = f"""fn main() {{
    println!("Hello from {name}!");
}}
"""
    
    (project_dir / 'src' / 'main.rs').write_text(main_rs)


def init_git_repo(project_dir: Path, language: str):
    """Initialize git repository."""
    try:
        subprocess.run(['git', 'init'], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(['git', 'add', '.'], cwd=project_dir, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=project_dir, check=True, capture_output=True)
        print_success("✅ Git repository initialized")
    except subprocess.CalledProcessError as e:
        print_warning(f"⚠️  Failed to initialize git repository: {e}")


def add_to_cache(config, name: str, project_dir: Path, category: str, language: str, framework: str):
    """Add project to shelly cache."""
    cache = config.cache
    repositories = cache.get('repositories', [])
    
    repo_info = {
        'name': name,
        'path': str(project_dir),
        'category': category,
        'url': None,  # Local project
        'language': language,
        'framework': framework,
        'created_with_shelly': True,
        'created_at': str(Path().cwd())  # Current timestamp would be better
    }
    
    repositories.append(repo_info)
    cache['repositories'] = repositories
    config.save_cache()


def show_next_steps(name: str, project_dir: Path, language: str, framework: str, orm: str):
    """Show next steps to the user."""
    print_info("\n🚀 Next steps:")
    
    print(f"  1. cd {project_dir}")
    
    if language in ['typescript', 'javascript']:
        print("  2. npm install")
        if framework == 'nestjs':
            print("  3. npm run start:dev")
        else:
            print("  3. npm run dev")
    elif language == 'python':
        print("  2. pip install -r requirements.txt")
        if framework == 'fastapi':
            print("  3. uvicorn app.main:app --reload")
        elif framework == 'django':
            print("  3. python manage.py runserver")
    elif language == 'go':
        print("  2. go mod tidy")
        print("  3. go run cmd/main.go")
    elif language == 'rust':
        print("  2. cargo build")
        print("  3. cargo run")
    
    if orm == 'prisma':
        print("  • Set up Prisma: npx prisma init")
    
    print(f"\n  Open with: shelly open {name}")


# Register the command
command = init
