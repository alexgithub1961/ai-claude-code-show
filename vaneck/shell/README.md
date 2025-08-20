# Shell Scripts Documentation

This directory contains shell scripts for building, running, and managing the VanEck ETF Data Downloader project.

## Scripts Overview

### `build.sh`
Builds the Docker image for the ETF downloader application.

#### Usage
```bash
./shell/build.sh [OPTIONS]

Options:
  --tag, -t TAG     Custom tag for the Docker image (default: vaneck-etf:latest)
  --no-cache        Build without using Docker cache
  --push            Push the image to registry after building
  --help, -h        Show help message
```

#### Examples
```bash
# Basic build
./shell/build.sh

# Build with custom tag
./shell/build.sh --tag vaneck-etf:v1.2.3

# Build without cache
./shell/build.sh --no-cache

# Build and push to registry
./shell/build.sh --tag myregistry/vaneck-etf:latest --push
```

#### Environment Variables Used
- `DOCKER_REGISTRY`: Docker registry URL (optional)
- `BUILD_ARGS`: Additional build arguments (optional)

### `run.sh`
Runs the ETF downloader in a Docker container with proper volume mounts and environment configuration.

#### Usage
```bash
./shell/run.sh [OPTIONS] [COMMAND]

Options:
  --data-dir DIR    Host directory for data storage (default: ./data)
  --config DIR      Host directory for configuration files (default: ./config)
  --logs DIR        Host directory for log files (default: ./logs)
  --env-file FILE   Environment file to load (default: .env)
  --detach, -d      Run container in background
  --interactive     Run container interactively
  --name NAME       Container name (default: vaneck-etf-downloader)
  --help, -h        Show help message

Commands:
  download          Download ETF data (default)
  validate          Validate configuration
  test             Run tests
  shell            Open interactive shell
```

#### Examples
```bash
# Basic run with default settings
./shell/run.sh

# Run with custom data directory
./shell/run.sh --data-dir /opt/etf-data

# Run in background
./shell/run.sh --detach

# Run interactively for debugging
./shell/run.sh --interactive shell

# Run with custom configuration
./shell/run.sh --config ./custom-config --env-file .env.prod

# Run validation only
./shell/run.sh validate
```

### `deploy.sh` (if present)
Deploys the application to production environment.

#### Usage
```bash
./shell/deploy.sh [ENVIRONMENT]

Environments:
  staging     Deploy to staging environment
  production  Deploy to production environment
```

## Environment Variables

### Docker Build Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DOCKER_REGISTRY` | Docker registry URL | - |
| `BUILD_ARGS` | Additional Docker build arguments | - |
| `DOCKER_BUILDKIT` | Enable BuildKit | `1` |

### Docker Run Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `CONTAINER_NAME` | Name for the Docker container | `vaneck-etf-downloader` |
| `HOST_DATA_DIR` | Host directory for data | `./data` |
| `HOST_CONFIG_DIR` | Host directory for config | `./config` |
| `HOST_LOGS_DIR` | Host directory for logs | `./logs` |

## Volume Mounting

The run script sets up the following volume mounts:

### Data Directory
```bash
-v ${HOST_DATA_DIR}:/app/data
```
- **Purpose**: Stores downloaded ETF data files
- **Permissions**: Read/write access required
- **Structure**: Organised by date and ETF symbol

### Configuration Directory
```bash
-v ${HOST_CONFIG_DIR}:/app/config:ro
```
- **Purpose**: Contains application configuration files
- **Permissions**: Read-only access
- **Files**: `config.yaml`, API keys, data source configurations

### Logs Directory
```bash
-v ${HOST_LOGS_DIR}:/app/logs
```
- **Purpose**: Application log files
- **Permissions**: Read/write access required
- **Rotation**: Logs are rotated daily

## Docker Network Configuration

### Default Network
The application runs on the default Docker bridge network unless specified otherwise.

### Custom Network (if required)
```bash
# Create custom network
docker network create etf-network

# Run with custom network
./shell/run.sh --network etf-network
```

## Security Considerations

### File Permissions
Ensure proper permissions on mounted directories:
```bash
# Set appropriate permissions
chmod 755 data/ config/ logs/
chmod 600 config/api_keys.env
```

### Environment Files
- Keep sensitive data in `.env` files
- Use `.env.example` for documentation
- Never commit actual API keys or passwords

### Container Security
- Runs as non-root user inside container
- Minimal base image (Alpine Linux)
- No unnecessary packages installed

## Troubleshooting

### Common Issues

#### Permission Errors
```bash
# Problem: Permission denied on mounted volumes
# Solution: Check directory permissions and ownership
ls -la data/ config/ logs/
sudo chown -R $USER:$USER data/ config/ logs/
```

#### Container Won't Start
```bash
# Problem: Container exits immediately
# Solution: Check logs for error messages
docker logs vaneck-etf-downloader

# Run in interactive mode for debugging
./shell/run.sh --interactive shell
```

#### Build Failures
```bash
# Problem: Docker build fails
# Solution: Clear Docker cache and rebuild
docker system prune
./shell/build.sh --no-cache
```

#### Network Issues
```bash
# Problem: Cannot reach external APIs
# Solution: Check network connectivity
docker run --rm vaneck-etf:latest curl -I https://api.example.com
```

### Debugging Commands

#### Check Container Status
```bash
docker ps -a | grep vaneck
docker inspect vaneck-etf-downloader
```

#### View Container Logs
```bash
docker logs vaneck-etf-downloader --follow
docker logs vaneck-etf-downloader --since 1h
```

#### Execute Commands in Running Container
```bash
docker exec -it vaneck-etf-downloader /bin/sh
docker exec vaneck-etf-downloader python src/validate_config.py
```

## Advanced Usage

### Multi-Stage Deployments
```bash
# Build for staging
./shell/build.sh --tag vaneck-etf:staging

# Deploy to staging
./shell/run.sh --env-file .env.staging --name vaneck-staging

# After validation, promote to production
docker tag vaneck-etf:staging vaneck-etf:production
./shell/run.sh --env-file .env.production --name vaneck-production
```

### Health Checks
```bash
# Check application health
curl http://localhost:8080/health

# Container health status
docker inspect vaneck-etf-downloader | grep -A 5 Health
```

### Performance Monitoring
```bash
# Container resource usage
docker stats vaneck-etf-downloader

# Detailed container information
docker exec vaneck-etf-downloader top
docker exec vaneck-etf-downloader df -h
```

## Script Maintenance

### Updating Scripts
When modifying shell scripts:
1. Test changes in development environment
2. Update documentation in this README
3. Ensure backwards compatibility where possible
4. Add appropriate error handling
5. Update version comments in script headers

### Version Control
All shell scripts are version controlled and should include:
- Header with script purpose and version
- Usage documentation
- Error handling
- Logging capabilities