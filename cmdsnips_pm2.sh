#!/usr/bin/env bash

set -euo pipefail

APP_NAME="CmdSnips"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_COMMAND="bash run.sh"

print_help() {
    echo "CmdSnips PM2 controller"
    echo ""
    echo "Usage:"
    echo "  AliLocalsnipp <command>"
    echo ""
    echo "Commands:"
    echo "  start    Start CmdSnips with PM2 (or restart if already registered)"
    echo "  stop     Stop CmdSnips process in PM2"
    echo "  restart  Restart CmdSnips process in PM2"
    echo "  status   Show PM2 status for CmdSnips"
    echo "  logs     Show PM2 logs for CmdSnips"
    echo "  delete   Delete CmdSnips from PM2"
    echo "  help     Show this help"
    echo ""
    echo "Examples:"
    echo "  AliLocalsnipp start"
    echo "  AliLocalsnipp stop"
    echo "  AliLocalsnipp status"
}

ensure_pm2() {
    if ! command -v pm2 >/dev/null 2>&1; then
        echo "Error: pm2 is not installed or not available in PATH."
        echo "Install it with: npm install -g pm2"
        exit 1
    fi
}

process_exists() {
    pm2 describe "$APP_NAME" >/dev/null 2>&1
}

start_process() {
    ensure_pm2
    cd "$SCRIPT_DIR"

    if process_exists; then
        pm2 restart "$APP_NAME"
    else
        pm2 start "$RUN_COMMAND" --name "$APP_NAME"
    fi
}

stop_process() {
    ensure_pm2
    if process_exists; then
        pm2 stop "$APP_NAME"
    else
        echo "Process '$APP_NAME' is not registered in PM2."
    fi
}

restart_process() {
    ensure_pm2
    if process_exists; then
        pm2 restart "$APP_NAME"
    else
        echo "Process '$APP_NAME' is not registered in PM2. Use 'start' first."
        exit 1
    fi
}

status_process() {
    ensure_pm2
    pm2 status "$APP_NAME"
}

logs_process() {
    ensure_pm2
    pm2 logs "$APP_NAME"
}

delete_process() {
    ensure_pm2
    if process_exists; then
        pm2 delete "$APP_NAME"
    else
        echo "Process '$APP_NAME' is not registered in PM2."
    fi
}

command="${1:-help}"

case "$command" in
    start)
        start_process
        ;;
    stop)
        stop_process
        ;;
    restart)
        restart_process
        ;;
    status)
        status_process
        ;;
    logs)
        logs_process
        ;;
    delete)
        delete_process
        ;;
    help|-h|--help)
        print_help
        ;;
    *)
        echo "Unknown command: $command"
        echo ""
        print_help
        exit 1
        ;;
esac
