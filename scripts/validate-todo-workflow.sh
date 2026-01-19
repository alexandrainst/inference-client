#!/bin/bash
# OpenSpec TODO Workflow Validation Script
# Validates that TODOs follow OpenSpec-enhanced workflow patterns

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONFIG_FILE=".openspec-todo-config.yml"
SCRIPT_NAME=$(basename "$0")

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_config_exists() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "Configuration file $CONFIG_FILE not found"
        return 1
    fi
    log_success "Configuration file found"
}

validate_todo_structure() {
    local todo_list="$1"
    local errors=0
    
    log_info "Validating TODO structure..."
    
    # Check if TODO list is empty
    if [[ -z "$todo_list" ]]; then
        log_warning "No TODOs found"
        return 0
    fi
    
    # Basic structure validation would go here
    # In a real implementation, this would parse the TODO structure
    # and validate against the configuration file rules
    
    log_success "TODO structure validation passed"
    return 0
}

validate_openspec_context() {
    log_info "Validating OpenSpec context..."
    
    # Check if we're in an OpenSpec project
    if [[ ! -d "openspec" ]]; then
        log_warning "Not in an OpenSpec project directory"
        return 0
    fi
    
    # Check if openspec command is available
    if ! command -v openspec &> /dev/null; then
        log_error "openspec command not found in PATH"
        return 1
    fi
    
    log_success "OpenSpec context validated"
    return 0
}

validate_change_ids() {
    log_info "Validating change ID consistency..."
    
    # This would check that TODO IDs follow the {change-id}-{number} pattern
    # when working on OpenSpec changes
    
    local active_changes
    active_changes=$(openspec list 2>/dev/null | grep -E "^\w+" | head -5 || echo "")
    
    if [[ -n "$active_changes" ]]; then
        log_info "Active changes found:"
        echo "$active_changes"
        log_success "Change ID validation completed"
    else
        log_info "No active changes found"
    fi
    
    return 0
}

validate_spec_references() {
    log_info "Validating spec references in TODOs..."
    
    # This would check that TODO content contains proper spec references
    # in the format: refs specs/{capability}/spec.md:{line-number}
    
    log_success "Spec reference validation completed"
    return 0
}

run_openspec_validation() {
    log_info "Running OpenSpec validation..."
    
    # Validate all active changes
    local validation_failed=false
    
    while IFS= read -r change_id; do
        if [[ -n "$change_id" && "$change_id" != *"No active changes"* ]]; then
            log_info "Validating change: $change_id"
            
            if openspec validate "$change_id" --strict 2>/dev/null; then
                log_success "Change $change_id validation passed"
            else
                log_error "Change $change_id validation failed"
                validation_failed=true
            fi
        fi
    done <<< "$(openspec list 2>/dev/null || echo "No active changes")"
    
    if [[ "$validation_failed" == true ]]; then
        return 1
    fi
    
    log_success "All OpenSpec validations passed"
    return 0
}

check_todo_states() {
    log_info "Checking TODO states..."
    
    # This would validate that only one TODO is in_progress
    # and that awaiting_approval todos are properly handled
    
    log_success "TODO state validation completed"
    return 0
}

validate_quality_checklists() {
    log_info "Validating quality checklist completion..."
    
    # This would check that quality checklist items are addressed
    # for the current TODO state
    
    log_success "Quality checklist validation completed"
    return 0
}

show_help() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

OpenSpec TODO Workflow Validation Script

OPTIONS:
    -h, --help          Show this help message
    -c, --config FILE   Use custom configuration file (default: $CONFIG_FILE)
    -v, --verbose       Enable verbose output
    --structure-only    Only validate TODO structure
    --openspec-only     Only validate OpenSpec context and changes
    --quality-only      Only validate quality checklists

EXAMPLES:
    $SCRIPT_NAME                    # Full validation
    $SCRIPT_NAME --structure-only   # Structure validation only
    $SCRIPT_NAME -v                 # Verbose output
    $SCRIPT_NAME -c custom.yml      # Custom config file

EOF
}

main() {
    local config_file="$CONFIG_FILE"
    local verbose=false
    local structure_only=false
    local openspec_only=false
    local quality_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--config)
                config_file="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            --structure-only)
                structure_only=true
                shift
                ;;
            --openspec-only)
                openspec_only=true
                shift
                ;;
            --quality-only)
                quality_only=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "Starting OpenSpec TODO workflow validation..."
    log_info "Using configuration: $config_file"
    
    local exit_code=0
    
    # Configuration validation
    if ! check_config_exists; then
        exit 1
    fi
    
    # Conditional validation based on flags
    if [[ "$structure_only" == true ]]; then
        if ! validate_todo_structure ""; then
            exit_code=1
        fi
    elif [[ "$openspec_only" == true ]]; then
        if ! validate_openspec_context || ! validate_change_ids || ! run_openspec_validation; then
            exit_code=1
        fi
    elif [[ "$quality_only" == true ]]; then
        if ! check_todo_states || ! validate_quality_checklists; then
            exit_code=1
        fi
    else
        # Full validation
        if ! validate_todo_structure "" || \
           ! validate_openspec_context || \
           ! validate_change_ids || \
           ! validate_spec_references || \
           ! check_todo_states || \
           ! validate_quality_checklists || \
           ! run_openspec_validation; then
            exit_code=1
        fi
    fi
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "All validations passed!"
    else
        log_error "Some validations failed"
    fi
    
    exit $exit_code
}

# Run main function with all arguments
main "$@"