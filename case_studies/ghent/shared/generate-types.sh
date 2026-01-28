#!/bin/bash

# Type Generation Script for ontEAUlogy
# This script generates TypeScript types from the FastAPI OpenAPI specification

set -e

echo "🔄 Starting type generation pipeline..."

# Configuration
SERVER_URL="http://localhost:8080"
OPENAPI_OUTPUT="shared/openapi.json"
TYPES_OUTPUT="frontend-react/src/api/generated-types.ts"
TIMEOUT=10

# Function to wait for server
wait_for_server() {
    echo "⏳ Waiting for server at $SERVER_URL..."
    for i in {1..30}; do
        if curl -s --connect-timeout 2 "$SERVER_URL/health" > /dev/null 2>&1; then
            echo "✅ Server is ready!"
            return 0
        fi
        echo "   Attempt $i/30..."
        sleep 2
    done
    
    echo "❌ Server not reachable after 60 seconds"
    echo "💡 Please start the server with: cd src/ghent_water/orchestrator && python main.py"
    exit 1
}

# Function to generate types
generate_types() {
    echo "📥 Exporting OpenAPI specification..."
    
    # Export OpenAPI from running server
    if ! curl -s --max-time $TIMEOUT "$SERVER_URL/openapi.json" > "$OPENAPI_OUTPUT"; then
        echo "❌ Failed to export OpenAPI specification"
        exit 1
    fi
    
    if [ ! -s "$OPENAPI_OUTPUT" ]; then
        echo "❌ OpenAPI export returned empty file"
        exit 1
    fi
    
    echo "✅ OpenAPI specification exported to $OPENAPI_OUTPUT"
    
    # Check if openapi-typescript is available
    if ! command -v npx &> /dev/null; then
        echo "❌ npx not found. Please install Node.js and npm."
        exit 1
    fi
    
    echo "🔧 Generating TypeScript types..."
    
    # Change to frontend directory and generate types
    cd frontend-react
    
    # Generate TypeScript types from OpenAPI
    if ! npx openapi-typescript "../$OPENAPI_OUTPUT" -o "$TYPES_OUTPUT"; then
        echo "❌ Failed to generate TypeScript types"
        exit 1
    fi
    
    # Check if types were generated
    if [ ! -f "$TYPES_OUTPUT" ]; then
        echo "❌ TypeScript types file not created"
        exit 1
    fi
    
    echo "✅ TypeScript types generated to $TYPES_OUTPUT"
    
    # Go back to original directory
    cd ..
    
    # Show type generation statistics
    echo "📊 Generation Statistics:"
    echo "   OpenAPI spec size: $(wc -c < "$OPENAPI_OUTPUT") bytes"
    echo "   TypeScript file size: $(wc -c < "$TYPES_OUTPUT") bytes"
    echo "   Number of type interfaces: $(grep -c "export interface" "$TYPES_OUTPUT" || echo "0")"
    
    # Run type check to verify generated types
    echo "🔍 Running type check..."
    cd frontend-react
    if npm run type-check; then
        echo "✅ Type check passed!"
    else
        echo "⚠️  Type check failed - check generated types for issues"
        cd ..
        return 1
    fi
    cd ..
}

# Function to clean up generated files
cleanup() {
    echo "🧹 Cleaning up generated files..."
    rm -f "$OPENAPI_OUTPUT" "$TYPES_OUTPUT"
    echo "✅ Cleanup completed"
}

# Function to show help
show_help() {
    echo "📖 Type Generation Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  generate    Generate TypeScript types from OpenAPI specification"
    echo "  wait        Wait for server to be ready"
    echo "  cleanup     Remove generated files"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 generate           # Generate types (waits for server if needed)"
    echo "  $0 wait              # Just wait for server"
    echo "  $0 cleanup            # Clean up generated files"
    echo ""
    echo "Environment variables:"
    echo "  SERVER_URL    Server URL (default: http://localhost:8080)"
    echo "  TIMEOUT       Request timeout in seconds (default: 10)"
}

# Main script logic
case "${1:-generate}" in
    "generate")
        wait_for_server
        generate_types
        ;;
    "wait")
        wait_for_server
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

echo "🎉 Type generation pipeline completed successfully!"