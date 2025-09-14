#!/bin/bash

# Simple Docker development script
# Usage: ./docker-dev.sh [start|stop|restart|logs|status]

set -e

COMPOSE_FILE="docker-compose.yml"

case "${1:-start}" in
    start)
        echo "🐳 Starting Conversation Simulator with Docker..."
        docker-compose -f $COMPOSE_FILE up --build -d
        echo "✅ Services started!"
        echo "📱 Frontend: http://localhost:3000"
        echo "🔧 Backend: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        ;;
    stop)
        echo "🛑 Stopping services..."
        docker-compose -f $COMPOSE_FILE down
        echo "✅ Services stopped!"
        ;;
    restart)
        echo "🔄 Restarting services..."
        docker-compose -f $COMPOSE_FILE restart
        echo "✅ Services restarted!"
        ;;
    logs)
        echo "📋 Showing logs..."
        docker-compose -f $COMPOSE_FILE logs -f
        ;;
    status)
        echo "📊 Service status:"
        docker-compose -f $COMPOSE_FILE ps
        ;;
    rebuild)
        echo "🔨 Rebuilding and starting services..."
        docker-compose -f $COMPOSE_FILE up --build -d
        echo "✅ Services rebuilt and started!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|rebuild}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show logs"
        echo "  status  - Show service status"
        echo "  rebuild - Rebuild and start services"
        exit 1
        ;;
esac

