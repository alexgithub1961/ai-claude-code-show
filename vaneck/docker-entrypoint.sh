#!/bin/sh

# VanEck ETF Data Downloader - Docker Entrypoint Script
# This script handles container initialization and configuration

set -e

# Default values
: ${DATA_DIR:="/app/data"}
: ${LOG_LEVEL:="INFO"}
: ${CONFIG_FILE:="/app/config/config.yaml"}

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ENTRYPOINT: $1"
}

# Ensure required directories exist
ensure_directories() {
    log "Ensuring required directories exist..."
    
    mkdir -p "$DATA_DIR"
    mkdir -p "/app/logs"
    
    # Set permissions
    chmod 755 "$DATA_DIR" "/app/logs"
    
    log "Directories created successfully"
}

# Validate configuration
validate_config() {
    log "Validating configuration..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        if [ -f "/app/config/config.yaml.example" ]; then
            log "No config file found, copying from example..."
            cp "/app/config/config.yaml.example" "$CONFIG_FILE"
        else
            log "ERROR: No configuration file found at $CONFIG_FILE"
            exit 1
        fi
    fi
    
    # Basic configuration validation
    if ! python -c "import yaml; yaml.safe_load(open('$CONFIG_FILE'))" 2>/dev/null; then
        log "ERROR: Configuration file is not valid YAML"
        exit 1
    fi
    
    log "Configuration validated successfully"
}

# Set up environment
setup_environment() {
    log "Setting up environment..."
    
    export PYTHONPATH="/app:$PYTHONPATH"
    export DATA_DIR
    export LOG_LEVEL
    export CONFIG_FILE
    
    log "Environment setup complete"
}

# Health check function
health_check() {
    log "Performing health check..."
    
    # Check if Python can import our modules
    if ! python -c "import sys; sys.path.insert(0, '/app'); import src.main" 2>/dev/null; then
        log "ERROR: Cannot import main application module"
        return 1
    fi
    
    # Check if we can access data directory
    if [ ! -w "$DATA_DIR" ]; then
        log "ERROR: Data directory is not writable: $DATA_DIR"
        return 1
    fi
    
    log "Health check passed"
    return 0
}

# Main initialization
main() {
    log "Starting VanEck ETF Data Downloader container..."
    log "Arguments: $*"
    
    # Run initialization steps
    ensure_directories
    validate_config
    setup_environment
    
    # Run health check
    if ! health_check; then
        log "ERROR: Health check failed"
        exit 1
    fi
    
    log "Initialization complete, starting application..."
    
    # If no command specified, run the default
    if [ $# -eq 0 ]; then
        exec python /app/src/main.py
    else
        exec python /app/src/main.py "$@"
    fi
}

# Handle special commands
case "$1" in
    "health")
        health_check
        exit $?
        ;;
    "config-check")
        validate_config
        log "Configuration is valid"
        exit 0
        ;;
    "version")
        python -c "import sys; sys.path.insert(0, '/app'); from src.main import main; main(['--version'])"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac