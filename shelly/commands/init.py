"""
Enhanced Project initialization command
Creates new projects with comprehensive file templates and configurations
"""

import click
import os
import json
from pathlib import Path
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
from .base import BaseCommand
from ..ui.display import print_success, print_error, print_info, print_warning
from ..ui.prompts import select_from_list, confirm_action


# Enhanced language and framework configurations
LANGUAGES = {
    'typescript': {
        'name': 'TypeScript',
        'frameworks': ['nestjs', 'express', 'fastify', 'koa'],
        'extensions': ['.ts', '.js'],
        'gitignore': 'Node',
        'package_manager': 'npm'
    },
    'javascript': {
        'name': 'JavaScript',
        'frameworks': ['express', 'fastify', 'koa', 'react', 'vue', 'svelte'],
        'extensions': ['.js', '.mjs'],
        'gitignore': 'Node',
        'package_manager': 'npm'
    },
    'python': {
        'name': 'Python',
        'frameworks': ['fastapi', 'django', 'flask', 'quart'],
        'extensions': ['.py'],
        'gitignore': 'Python',
        'package_manager': 'pip'
    },
    'go': {
        'name': 'Go',
        'frameworks': ['gin', 'echo', 'fiber', 'chi'],
        'extensions': ['.go'],
        'gitignore': 'Go',
        'package_manager': 'go'
    },
    'rust': {
        'name': 'Rust',
        'frameworks': ['axum', 'warp', 'actix-web', 'rocket'],
        'extensions': ['.rs'],
        'gitignore': 'Rust',
        'package_manager': 'cargo'
    },
    'java': {
        'name': 'Java',
        'frameworks': ['spring-boot', 'quarkus', 'micronaut'],
        'extensions': ['.java'],
        'gitignore': 'Java',
        'package_manager': 'maven'
    }
}

# Enhanced ORM/Database options with versions
ORMS = {
    'typescript': [
        {'name': 'prisma', 'package': '@prisma/client', 'dev_package': 'prisma'},
        {'name': 'typeorm', 'package': 'typeorm', 'dev_package': None},
        {'name': 'drizzle', 'package': 'drizzle-orm', 'dev_package': 'drizzle-kit'},
        {'name': 'mongoose', 'package': 'mongoose', 'dev_package': '@types/mongoose'}
    ],
    'python': [
        {'name': 'sqlalchemy', 'package': 'sqlalchemy', 'dev_package': 'alembic'},
        {'name': 'tortoise-orm', 'package': 'tortoise-orm', 'dev_package': None},
        {'name': 'prisma', 'package': 'prisma', 'dev_package': None}
    ],
    'go': [
        {'name': 'gorm', 'package': 'gorm.io/gorm', 'dev_package': None},
        {'name': 'sqlx', 'package': 'github.com/jmoiron/sqlx', 'dev_package': None}
    ],
    'rust': [
        {'name': 'diesel', 'package': 'diesel', 'dev_package': None},
        {'name': 'sqlx', 'package': 'sqlx', 'dev_package': None},
        {'name': 'sea-orm', 'package': 'sea-orm', 'dev_package': None}
    ]
}

# Enhanced project types with specific templates
PROJECT_TYPES = {
    'api': {
        'name': 'REST API',
        'description': 'RESTful API with standard CRUD operations',
        'features': ['health_check', 'swagger', 'cors', 'validation', 'logging']
    },
    'microservice': {
        'name': 'Microservice',
        'description': 'Microservice with event handling and service discovery',
        'features': ['health_check', 'metrics', 'events', 'config', 'logging', 'tracing']
    },
    'monolith': {
        'name': 'Monolithic Application',
        'description': 'Full-featured monolithic application',
        'features': ['health_check', 'swagger', 'auth', 'database', 'caching', 'logging']
    },
    'graphql': {
        'name': 'GraphQL API',
        'description': 'GraphQL API with schema-first approach',
        'features': ['health_check', 'playground', 'validation', 'logging']
    },
    'cli': {
        'name': 'Command Line Tool',
        'description': 'CLI application with subcommands',
        'features': ['config', 'logging', 'help']
    },
    'library': {
        'name': 'Library/Package',
        'description': 'Reusable library or package',
        'features': ['testing', 'documentation', 'ci']
    }
}

# Docker configurations
DOCKER_CONFIGS = {
    'typescript': {
        'base_image': 'node:18-alpine',
        'port': 3000,
        'health_check': '/health'
    },
    'python': {
        'base_image': 'python:3.11-slim',
        'port': 8000,
        'health_check': '/health'
    },
    'go': {
        'base_image': 'golang:1.21-alpine',
        'port': 8080,
        'health_check': '/health'
    },
    'rust': {
        'base_image': 'rust:1.70-alpine',
        'port': 8000,
        'health_check': '/health'
    }
}


@click.command()
@click.argument('name', required=False)
@click.option('--language', '-l', help='Programming language (typescript, python, go, etc.)')
@click.option('--framework', '-f', help='Framework to use')
@click.option('--orm', help='ORM/Database library to use')
@click.option('--type', 'project_type', help='Project type (api, microservice, etc.)')
@click.option('--git/--no-git', default=True, help='Initialize git repository')
@click.option('--docker/--no-docker', default=True, help='Add Docker configuration')
@click.option('--ci/--no-ci', default=False, help='Add CI/CD configuration')
@click.option('--category', '-c', help='Category for the project')
@click.option('--dir', 'custom_dir', help='Custom directory to create project in')
@click.option('--database', help='Database type (postgresql, mysql, mongodb, etc.)')
@click.option('--auth', help='Authentication method (jwt, oauth, basic)')
def init(name, language, framework, orm, project_type, git, docker, ci, category, custom_dir, database, auth):
    """Initialize a new project with comprehensive structure and configurations.
    
    Examples:
      shelly init my-api --language typescript --framework nestjs --orm prisma --database postgresql
      shelly init microservice --type microservice --language go --framework gin --docker
      shelly init my-project  # Interactive mode
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
            display_func=lambda x: PROJECT_TYPES[x]['name']
        )
    
    # Enhanced ORM selection with descriptions
    if not orm and language in ORMS and project_type in ['api', 'microservice', 'monolith']:
        orm_options = ORMS[language]
        if orm_options:
            orm_names = [o['name'] for o in orm_options] + ['none']
            orm = select_from_list(
                f"Select ORM/Database library:",
                orm_names
            )
            if orm == 'none':
                orm = None
    
    # Database selection
    if not database and orm:
        databases = ['postgresql', 'mysql', 'sqlite', 'mongodb', 'redis']
        database = select_from_list(
            "Select database type:",
            databases + ['skip']
        )
        if database == 'skip':
            database = None
    
    # Auth selection for APIs
    if not auth and project_type in ['api', 'microservice', 'monolith']:
        auth_options = ['jwt', 'oauth', 'basic', 'none']
        auth = select_from_list(
            "Select authentication method:",
            auth_options
        )
        if auth == 'none':
            auth = None
    
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
    print_info(f"🚀 Creating {LANGUAGES[language]['name']} {PROJECT_TYPES[project_type]['name']} project...")
    print_info(f"📁 Location: {project_dir}")
    
    try:
        # Create directory structure
        create_project_structure(project_dir, language, framework, orm, project_type)
        
        # Create comprehensive files
        create_comprehensive_files(project_dir, name, language, framework, orm, project_type, database, auth)
        
        # Create Docker configuration
        if docker:
            create_docker_files(project_dir, name, language, framework, project_type)
        
        # Create CI/CD configuration
        if ci:
            create_ci_files(project_dir, language, framework)
        
        # Initialize git if requested
        if git:
            init_git_repo(project_dir, language)
        
        # Add to shelly cache
        add_to_cache(config, name, project_dir, category, language, framework)
        
        print_success(f"✅ Project '{name}' created successfully!")
        print_info(f"📍 Location: {project_dir}")
        
        # Show project summary
        show_project_summary(name, language, framework, orm, project_type, database, auth, docker, ci)
        
        # Show next steps
        show_next_steps(name, project_dir, language, framework, orm)
        
    except Exception as e:
        print_error(f"Failed to create project: {str(e)}")


def create_comprehensive_files(project_dir: Path, name: str, language: str, framework: str, 
                             orm: str, project_type: str, database: str, auth: str):
    """Create comprehensive configuration and template files."""
    
    # Create README.md with enhanced content
    create_enhanced_readme(project_dir, name, language, framework, orm, project_type, database, auth)
    
    # Create .gitignore
    create_gitignore(project_dir, language)
    
    # Create environment files
    create_env_files(project_dir, language, framework, database, auth)
    
    # Create language-specific files with templates
    if language in ['typescript', 'javascript']:
        create_nodejs_files(project_dir, name, language, framework, orm, project_type, database, auth)
        create_nodejs_templates(project_dir, framework, orm, project_type, auth)
    elif language == 'python':
        create_python_files(project_dir, name, framework, orm, project_type, database, auth)
        create_python_templates(project_dir, framework, orm, project_type, auth)
    elif language == 'go':
        create_go_files(project_dir, name, framework, project_type, database, auth)
        create_go_templates(project_dir, framework, project_type, auth)
    elif language == 'rust':
        create_rust_files(project_dir, name, framework, project_type, database, auth)
        create_rust_templates(project_dir, framework, project_type, auth)
    
    # Create configuration files
    create_config_files(project_dir, language, framework, project_type)
    
    # Create test files
    create_test_files(project_dir, language, framework, project_type)


def create_nodejs_templates(project_dir: Path, framework: str, orm: str, project_type: str, auth: str):
    """Create Node.js/TypeScript template files."""
    
    if framework == 'nestjs':
        create_nestjs_templates(project_dir, orm, project_type, auth)
    elif framework == 'express':
        create_express_templates(project_dir, orm, project_type, auth)


def create_nestjs_templates(project_dir: Path, orm: str, project_type: str, auth: str):
    """Create NestJS template files."""
    
    # Main application file
    main_ts = '''import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Global validation pipe
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }));
  
  // CORS
  app.enableCors();
  
  // Swagger documentation
  const config = new DocumentBuilder()
    .setTitle('API Documentation')
    .setDescription('API description')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);
  
  const port = process.env.PORT || 3000;
  await app.listen(port);
  
  console.log(`🚀 Application is running on: http://localhost:${port}`);
  console.log(`📚 Swagger UI: http://localhost:${port}/api`);
}

bootstrap();
'''
    (project_dir / 'src' / 'main.ts').write_text(main_ts)
    
    # App module
    app_module = '''import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { HealthModule } from './modules/health/health.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    HealthModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
'''
    (project_dir / 'src' / 'app.module.ts').write_text(app_module)
    
    # App controller
    app_controller = '''import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { AppService } from './app.service';

@ApiTags('App')
@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  @ApiOperation({ summary: 'Get application info' })
  getHello(): string {
    return this.appService.getHello();
  }
}
'''
    (project_dir / 'src' / 'app.controller.ts').write_text(app_controller)
    
    # App service
    app_service = '''import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): string {
    return 'Hello World!';
  }
}
'''
    (project_dir / 'src' / 'app.service.ts').write_text(app_service)
    
    # Health module
    health_module = '''import { Module } from '@nestjs/common';
import { TerminusModule } from '@nestjs/terminus';
import { HealthController } from './health.controller';

@Module({
  imports: [TerminusModule],
  controllers: [HealthController],
})
export class HealthModule {}
'''
    (project_dir / 'src' / 'modules' / 'health' / 'health.module.ts').write_text(health_module)
    
    # Health controller
    health_controller = '''import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { HealthCheck, HealthCheckService, HttpHealthIndicator } from '@nestjs/terminus';

@ApiTags('Health')
@Controller('health')
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private http: HttpHealthIndicator,
  ) {}

  @Get()
  @ApiOperation({ summary: 'Health check' })
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.http.pingCheck('basic', 'http://localhost:3000'),
    ]);
  }
}
'''
    (project_dir / 'src' / 'modules' / 'health' / 'health.controller.ts').write_text(health_controller)
    
    # Common DTOs
    base_dto = '''import { ApiProperty } from '@nestjs/swagger';

export class BaseResponseDto {
  @ApiProperty()
  success: boolean;

  @ApiProperty()
  message: string;

  @ApiProperty()
  timestamp: Date;

  constructor(success: boolean, message: string) {
    this.success = success;
    this.message = message;
    this.timestamp = new Date();
  }
}
'''
    (project_dir / 'src' / 'common' / 'dto' / 'base-response.dto.ts').write_text(base_dto)
    
    # Global exception filter
    exception_filter = '''import { 
  ExceptionFilter, 
  Catch, 
  ArgumentsHost, 
  HttpException,
  HttpStatus 
} from '@nestjs/common';
import { Request, Response } from 'express';

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;

    const message = exception instanceof HttpException
      ? exception.getResponse()
      : 'Internal server error';

    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      error: message,
    });
  }
}
'''
    (project_dir / 'src' / 'common' / 'filters' / 'all-exceptions.filter.ts').write_text(exception_filter)
    
    # Create directories
    (project_dir / 'src' / 'common' / 'dto').mkdir(parents=True, exist_ok=True)
    (project_dir / 'src' / 'modules' / 'health').mkdir(parents=True, exist_ok=True)


def create_docker_files(project_dir: Path, name: str, language: str, framework: str, project_type: str):
    """Create Docker configuration files."""
    
    docker_config = DOCKER_CONFIGS.get(language, {})
    base_image = docker_config.get('base_image', 'ubuntu:20.04')
    port = docker_config.get('port', 8000)
    
    if language in ['typescript', 'javascript']:
        dockerfile = f'''# Build stage
FROM {base_image} AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM {base_image} AS production

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 --gid 1001 nestjs

# Copy built application
COPY --from=builder --chown=nestjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nestjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nestjs:nodejs /app/package*.json ./

USER nestjs

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/health || exit 1

CMD ["node", "dist/main.js"]
'''
    elif language == 'python':
        dockerfile = f'''# Build stage
FROM {base_image} AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM {base_image} AS production

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1001 python && \\
    useradd --uid 1001 --gid python --shell /bin/bash python

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
COPY --chown=python:python . .

USER python

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/health || exit 1

CMD ["python", "-m", "app.main"]
'''
    elif language == 'go':
        dockerfile = f'''# Build stage
FROM {base_image} AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd

# Production stage
FROM alpine:latest AS production

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates curl

WORKDIR /root/

# Copy binary from builder
COPY --from=builder /app/main .

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/health || exit 1

CMD ["./main"]
'''
    
    (project_dir / 'Dockerfile').write_text(dockerfile)
    
    # Docker compose file
    compose_content = f'''version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "{port}:{port}"
    environment:
      - NODE_ENV=development
      - PORT={port}
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: {name}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
'''
    
    (project_dir / 'docker-compose.yml').write_text(compose_content)
    
    # .dockerignore
    dockerignore = '''node_modules
npm-debug.log
Dockerfile
.dockerignore
.git
.gitignore
README.md
.env
.env.local
.nyc_output
coverage
.pytest_cache
__pycache__
.DS_Store
'''
    
    (project_dir / '.dockerignore').write_text(dockerignore)


def create_env_files(project_dir: Path, language: str, framework: str, database: str, auth: str):
    """Create environment configuration files."""
    
    env_content = f'''# Application
NODE_ENV=development
PORT=3000

# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/myapp"
REDIS_URL="redis://localhost:6379"

# Authentication
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRES_IN=7d

# External APIs
API_KEY=your-api-key

# Logging
LOG_LEVEL=debug
'''
    
    env_example = env_content.replace('your-super-secret-jwt-key', 'change-me-in-production')
    env_example = env_example.replace('your-api-key', 'your-api-key-here')
    
    (project_dir / '.env').write_text(env_content)
    (project_dir / '.env.example').write_text(env_example)


def create_ci_files(project_dir: Path, language: str, framework: str):
    """Create CI/CD configuration files."""
    
    # GitHub Actions workflow
    github_dir = project_dir / '.github' / 'workflows'
    github_dir.mkdir(parents=True, exist_ok=True)
    
    if language in ['typescript', 'javascript']:
        ci_content = '''name: CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint
    
    - name: Run tests
      run: npm run test:cov
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
    
    - name: Build
      run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build and push Docker image
      run: |
        echo "Deploy to production"
        # Add your deployment steps here
'''
    elif language == 'python':
        ci_content = '''name: CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest --cov=app tests/
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
'''
    
    (github_dir / 'ci.yml').write_text(ci_content)


def show_project_summary(name: str, language: str, framework: str, orm: str, 
                        project_type: str, database: str, auth: str, docker: bool, ci: bool):
    """Show a summary of the created project."""
    
    print_info(f"\n📋 Project Summary:")
    print_info(f"Name: {name}")
    print_info(f"Language: {LANGUAGES[language]['name']}")
    if framework:
        print_info(f"Framework: {framework}")
    if orm:
        print_info(f"ORM: {orm}")
    print_info(f"Project Type: {PROJECT_TYPES[project_type]['name']}")
    if database:
        print_info(f"Database: {database}")
    if auth:
        print_info(f"Authentication: {auth}")
    print_info(f"Docker: {'Enabled' if docker else 'Disabled'}")
    print_info(f"CI/CD: {'Enabled' if ci else 'Disabled'}")


# Missing functions implementation
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


def create_enhanced_readme(project_dir: Path, name: str, language: str, framework: str, 
                         orm: str, project_type: str, database: str, auth: str):
    """Create enhanced README.md file."""
    
    # Get project info
    lang_info = LANGUAGES.get(language, {})
    project_info = PROJECT_TYPES.get(project_type, {})
    
    content = f"""# {name.title()}

{project_info.get('description', 'Project')} built with {lang_info.get('name', language)}"""
    
    if framework:
        content += f" and {framework.title()}"
    
    content += f"""

## Description

{project_info.get('description', 'TODO: Add project description')}

## Tech Stack

- **Language**: {lang_info.get('name', language)}"""
    
    if framework:
        content += f"\n- **Framework**: {framework.title()}"
    
    if orm:
        content += f"\n- **ORM/Database**: {orm.title()}"
    
    if database:
        content += f"\n- **Database**: {database.title()}"
    
    if auth:
        content += f"\n- **Authentication**: {auth.upper()}"
    
    # Add features section
    features = project_info.get('features', [])
    if features:
        content += f"\n\n## Features\n\n"
        feature_descriptions = {
            'health_check': '🏥 Health Check endpoints',
            'swagger': '📚 API Documentation (Swagger/OpenAPI)',
            'cors': '🌐 CORS configuration',
            'validation': '✅ Request validation',
            'logging': '📝 Structured logging',
            'metrics': '📊 Metrics collection',
            'events': '🔄 Event handling',
            'config': '⚙️ Configuration management',
            'tracing': '🔍 Distributed tracing',
            'auth': '🔐 Authentication & authorization',
            'database': '🗄️ Database integration',
            'caching': '⚡ Caching layer',
            'playground': '🎮 GraphQL Playground',
            'help': '❓ Help system',
            'testing': '🧪 Testing framework',
            'documentation': '📖 Documentation',
            'ci': '🚀 CI/CD pipeline'
        }
        
        for feature in features:
            desc = feature_descriptions.get(feature, f'• {feature.title()}')
            content += f"- {desc}\n"
    
    content += f"""

## Getting Started

### Prerequisites

- {lang_info.get('name', language)} {get_language_version(language)}"""
    
    if framework:
        content += f"\n- {framework.title()}"
    
    if database:
        content += f"\n- {database.title()} database"
    
    content += f"""

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {name}

# Install dependencies
{get_install_command(language)}
```

### Environment Setup

```bash
# Copy environment file
cp .env.example .env

# Edit environment variables
# Update database credentials, API keys, etc.
```

### Running the Application

```bash
# Development mode
{get_dev_command(language, framework)}

# Production mode
{get_prod_command(language, framework)}
```

## Development

### Project Structure

```
{name}/
├── {get_src_dir(language)}/          # Source code
├── tests/              # Test files
├── docs/               # Documentation"""
    
    if language in ['typescript', 'javascript']:
        content += f"""
├── package.json        # Dependencies and scripts
├── tsconfig.json       # TypeScript configuration"""
    elif language == 'python':
        content += f"""
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Project configuration"""
    elif language == 'go':
        content += f"""
├── go.mod             # Go module definition
├── cmd/               # Main applications"""
    elif language == 'rust':
        content += f"""
├── Cargo.toml         # Rust package configuration
├── src/               # Source code"""
    
    content += f"""
├── .env.example       # Environment variables template
└── README.md          # This file
```

### Testing

```bash
{get_test_command(language, framework)}
```

### Linting and Formatting

```bash
{get_lint_command(language, framework)}
```

## API Documentation

"""
    
    if framework == 'nestjs':
        content += "Visit `http://localhost:3000/api` for Swagger documentation when the server is running."
    elif 'api' in project_type:
        content += "API documentation will be available when the server is running."
    else:
        content += "Documentation for this project type will be added here."
    
    content += f"""

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

TODO: Add license information

---

*Generated with ❤️ by [Shelly CLI](https://github.com/Domains18/shelly)*
"""
    
    (project_dir / 'README.md').write_text(content)


def get_language_version(language: str) -> str:
    """Get recommended language version."""
    versions = {
        'typescript': '4.9+',
        'javascript': 'ES2020+',
        'python': '3.11+',
        'go': '1.21+',
        'rust': '1.70+',
        'java': '17+'
    }
    return versions.get(language, 'latest')


def get_src_dir(language: str) -> str:
    """Get source directory name for language."""
    return 'app' if language == 'python' else 'src'


def get_install_command(language: str) -> str:
    """Get install command for language."""
    commands = {
        'typescript': 'npm install',
        'javascript': 'npm install',
        'python': 'pip install -r requirements.txt',
        'go': 'go mod tidy',
        'rust': 'cargo build',
        'java': 'mvn install'
    }
    return commands.get(language, 'echo "Add install command"')


def get_dev_command(language: str, framework: str) -> str:
    """Get development command."""
    if language in ['typescript', 'javascript']:
        if framework == 'nestjs':
            return 'npm run start:dev'
        return 'npm run dev'
    elif language == 'python':
        if framework == 'fastapi':
            return 'uvicorn app.main:app --reload'
        elif framework == 'django':
            return 'python manage.py runserver'
        return 'python -m app.main'
    elif language == 'go':
        return 'go run cmd/main.go'
    elif language == 'rust':
        return 'cargo run'
    return 'echo "Add dev command"'


def get_prod_command(language: str, framework: str) -> str:
    """Get production command."""
    if language in ['typescript', 'javascript']:
        return 'npm run start:prod'
    elif language == 'python':
        if framework == 'fastapi':
            return 'uvicorn app.main:app'
        return 'python -m app.main'
    elif language == 'go':
        return './main'
    elif language == 'rust':
        return 'cargo run --release'
    return 'echo "Add prod command"'


def get_test_command(language: str, framework: str) -> str:
    """Get test command."""
    if language in ['typescript', 'javascript']:
        return 'npm test'
    elif language == 'python':
        return 'pytest'
    elif language == 'go':
        return 'go test ./...'
    elif language == 'rust':
        return 'cargo test'
    return 'echo "Add test command"'


def get_lint_command(language: str, framework: str) -> str:
    """Get lint command."""
    if language in ['typescript', 'javascript']:
        return 'npm run lint'
    elif language == 'python':
        return 'flake8 . && black --check .'
    elif language == 'go':
        return 'golangci-lint run'
    elif language == 'rust':
        return 'cargo clippy'
    return 'echo "Add lint command"'


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


def create_nodejs_files(project_dir: Path, name: str, language: str, framework: str, orm: str, 
                       project_type: str, database: str, auth: str):
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
            "test": "jest",
            "test:watch": "jest --watch",
            "test:cov": "jest --coverage",
            "lint": "eslint \"{src,apps,libs,test}/**/*.ts\" --fix",
            "format": "prettier --write \"src/**/*.ts\" \"test/**/*.ts\""
        },
        "keywords": [],
        "author": "",
        "license": "MIT",
        "devDependencies": {
            "@types/node": "^20.0.0",
            "typescript": "^5.0.0",
            "ts-node-dev": "^2.0.0",
            "jest": "^29.0.0",
            "@types/jest": "^29.0.0",
            "eslint": "^8.0.0",
            "@typescript-eslint/eslint-plugin": "^6.0.0",
            "@typescript-eslint/parser": "^6.0.0",
            "prettier": "^3.0.0"
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
            "test:e2e": "jest --config ./test/jest-e2e.json"
        })
        package_json["dependencies"].update({
            "@nestjs/common": "^10.0.0",
            "@nestjs/core": "^10.0.0",
            "@nestjs/platform-express": "^10.0.0",
            "@nestjs/config": "^3.0.0",
            "@nestjs/swagger": "^7.0.0",
            "@nestjs/terminus": "^10.0.0",
            "reflect-metadata": "^0.1.13",
            "rxjs": "^7.0.0",
            "class-validator": "^0.14.0",
            "class-transformer": "^0.5.0"
        })
        package_json["devDependencies"]["@nestjs/cli"] = "^10.0.0"
        package_json["devDependencies"]["@nestjs/schematics"] = "^10.0.0"
        package_json["devDependencies"]["@nestjs/testing"] = "^10.0.0"
    elif framework == 'express':
        package_json["dependencies"].update({
            "express": "^4.18.0",
            "cors": "^2.8.5",
            "helmet": "^7.0.0"
        })
        package_json["devDependencies"]["@types/express"] = "^4.17.0"
        package_json["devDependencies"]["@types/cors"] = "^2.8.0"
    
    # Add ORM dependencies
    if orm and language in ORMS:
        orm_configs = ORMS[language]
        orm_config = next((o for o in orm_configs if o['name'] == orm), None)
        if orm_config:
            package_json["dependencies"][orm_config['package']] = "^5.0.0"
            if orm_config['dev_package']:
                package_json["devDependencies"][orm_config['dev_package']] = "^5.0.0"
    
    # Add auth dependencies
    if auth == 'jwt':
        package_json["dependencies"]["jsonwebtoken"] = "^9.0.0"
        package_json["devDependencies"]["@types/jsonwebtoken"] = "^9.0.0"
        if framework == 'nestjs':
            package_json["dependencies"]["@nestjs/jwt"] = "^10.0.0"
            package_json["dependencies"]["@nestjs/passport"] = "^10.0.0"
            package_json["dependencies"]["passport-jwt"] = "^4.0.0"
    
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


def create_python_files(project_dir: Path, name: str, framework: str, orm: str, 
                       project_type: str, database: str, auth: str):
    """Create Python specific files."""
    
    # requirements.txt
    requirements = []
    
    if framework == 'fastapi':
        requirements.extend(['fastapi', 'uvicorn[standard]', 'pydantic'])
    elif framework == 'django':
        requirements.append('django')
    elif framework == 'flask':
        requirements.append('flask')
    
    if orm == 'sqlalchemy':
        requirements.extend(['sqlalchemy', 'alembic'])
    elif orm == 'django-orm' and framework == 'django':
        pass  # Already included with Django
    
    if auth == 'jwt':
        requirements.append('pyjwt')
    
    if database == 'postgresql':
        requirements.append('psycopg2-binary')
    elif database == 'mysql':
        requirements.append('pymysql')
    elif database == 'mongodb':
        requirements.append('pymongo')
    
    requirements.extend(['python-dotenv', 'pytest', 'requests'])
    
    (project_dir / 'requirements.txt').write_text('\n'.join(requirements) + '\n')
    
    # requirements-dev.txt
    dev_requirements = [
        'pytest',
        'pytest-cov',
        'black',
        'flake8',
        'mypy',
        'pre-commit'
    ]
    
    (project_dir / 'requirements-dev.txt').write_text('\n'.join(dev_requirements) + '\n')
    
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
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "black", "flake8", "mypy"]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
"""
    
    (project_dir / 'pyproject.toml').write_text(pyproject)


def create_go_files(project_dir: Path, name: str, framework: str, project_type: str, database: str, auth: str):
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
    "log"
    "net/http"
)

func main() {{
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {{
        fmt.Fprintf(w, "Hello from {name}!")
    }})
    
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {{
        w.Header().Set("Content-Type", "application/json")
        fmt.Fprintf(w, `{{"status": "ok", "service": "{name}"}}`)
    }})
    
    port := ":8080"
    fmt.Printf("🚀 Server starting on http://localhost%s\\n", port)
    log.Fatal(http.ListenAndServe(port, nil))
}}
"""
    
    (project_dir / 'cmd' / 'main.go').write_text(main_go)


def create_rust_files(project_dir: Path, name: str, framework: str, project_type: str, database: str, auth: str):
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
serde = { version = "1.0", features = ["derive"] }
"""
    
    (project_dir / 'Cargo.toml').write_text(cargo_toml)
    
    # main.rs
    main_rs = f"""fn main() {{
    println!("Hello from {name}!");
}}
"""
    
    (project_dir / 'src' / 'main.rs').write_text(main_rs)


def create_express_templates(project_dir: Path, orm: str, project_type: str, auth: str):
    """Create Express.js template files."""
    
    # Basic Express app
    app_js = '''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Hello World!' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(port, () => {
  console.log(`🚀 Server running on http://localhost:${port}`);
});
'''
    
    (project_dir / 'src' / 'app.ts').write_text(app_js)


def create_python_templates(project_dir: Path, framework: str, orm: str, project_type: str, auth: str):
    """Create Python template files."""
    
    if framework == 'fastapi':
        # FastAPI main app
        main_py = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        (project_dir / 'app' / 'main.py').write_text(main_py)
        
        # __init__.py files
        (project_dir / 'app' / '__init__.py').write_text('')
        (project_dir / 'app' / 'api' / '__init__.py').write_text('')
        (project_dir / 'app' / 'api' / 'v1' / '__init__.py').write_text('')


def create_go_templates(project_dir: Path, framework: str, project_type: str, auth: str):
    """Create Go template files."""
    
    if framework == 'gin':
        # Update main.go for Gin
        main_go = '''package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    
    r.GET("/", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "message": "Hello World!",
        })
    })
    
    r.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "status": "ok",
        })
    })
    
    r.Run(":8080")
}
'''
        (project_dir / 'cmd' / 'main.go').write_text(main_go)


def create_rust_templates(project_dir: Path, framework: str, project_type: str, auth: str):
    """Create Rust template files."""
    
    if framework == 'axum':
        # Update main.rs for Axum
        main_rs = '''use axum::{
    response::Json,
    routing::get,
    Router,
};
use serde_json::{json, Value};

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(root))
        .route("/health", get(health));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8000").await.unwrap();
    println!("🚀 Server running on http://localhost:8000");
    axum::serve(listener, app).await.unwrap();
}

async fn root() -> Json<Value> {
    Json(json!({ "message": "Hello World!" }))
}

async fn health() -> Json<Value> {
    Json(json!({ "status": "ok" }))
}
'''
        (project_dir / 'src' / 'main.rs').write_text(main_rs)


def create_config_files(project_dir: Path, language: str, framework: str, project_type: str):
    """Create configuration files."""
    
    if language in ['typescript', 'javascript']:
        # .eslintrc.js
        eslint_config = '''{
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "project": "tsconfig.json",
    "sourceType": "module"
  },
  "plugins": ["@typescript-eslint/eslint-plugin"],
  "extends": [
    "@typescript-eslint/recommended"
  ],
  "root": true,
  "env": {
    "node": true,
    "jest": true
  },
  "ignorePatterns": [".eslintrc.js"],
  "rules": {
    "@typescript-eslint/interface-name-prefix": "off",
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "off"
  }
}
'''
        (project_dir / '.eslintrc.json').write_text(eslint_config)
        
        # .prettierrc
        prettier_config = '''{
  "singleQuote": true,
  "trailingComma": "all",
  "semi": true,
  "tabWidth": 2,
  "printWidth": 80
}
'''
        (project_dir / '.prettierrc').write_text(prettier_config)


def create_test_files(project_dir: Path, language: str, framework: str, project_type: str):
    """Create test files."""
    
    if language in ['typescript', 'javascript'] and framework == 'nestjs':
        # Jest configuration
        jest_config = '''{
  "moduleFileExtensions": ["js", "json", "ts"],
  "rootDir": "src",
  "testRegex": ".*\\\\.spec\\\\.ts$",
  "transform": {
    "^.+\\\\.(t|j)s$": "ts-jest"
  },
  "collectCoverageFrom": [
    "**/*.(t|j)s"
  ],
  "coverageDirectory": "../coverage",
  "testEnvironment": "node"
}
'''
        (project_dir / 'package.json.jest').write_text(jest_config)
        
        # App controller test
        app_test = '''import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('root', () => {
    it('should return "Hello World!"', () => {
      expect(appController.getHello()).toBe('Hello World!');
    });
  });
});
'''
        (project_dir / 'src' / 'app.controller.spec.ts').write_text(app_test)


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
        'created_at': datetime.now().isoformat()
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