#!/bin/bash

# Script para configurar AI Provider
echo "🔧 Configurando AI Provider para Conversation Simulator..."

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp env.example .env
    echo "✅ Archivo .env creado desde env.example"
else
    echo "⚠️  Archivo .env ya existe"
fi

# Función para configurar provider
configure_provider() {
    local provider=$1
    local api_key_var=$2
    
    echo "🔧 Configurando $provider como AI provider..."
    
    # Actualizar AI_PROVIDER
    if grep -q "AI_PROVIDER=" .env; then
        sed -i.bak "s/AI_PROVIDER=.*/AI_PROVIDER=$provider/" .env
    else
        echo "AI_PROVIDER=$provider" >> .env
    fi
    
    echo "✅ $provider configurado como AI provider"
    echo ""
    echo "🎯 Próximos pasos:"
    echo "1. Edita el archivo .env y agrega tu $api_key_var"
    echo "2. Ejecuta: docker-compose up --build"
    echo "3. El sistema usará $provider para las conversaciones"
    echo ""
}

# Mostrar opciones
echo "🤖 Selecciona tu AI Provider:"
echo "1) OpenAI (GPT-4o-mini) - Recomendado para testing"
echo "2) Claude (Sonnet 4) - Recomendado para producción"
echo "3) Solo mostrar configuración actual"
echo ""

read -p "Ingresa tu opción (1-3): " choice

case $choice in
    1)
        configure_provider "openai" "OPENAI_API_KEY"
        ;;
    2)
        configure_provider "claude" "ANTHROPIC_API_KEY"
        ;;
    3)
        echo "📋 Configuración actual:"
        if [ -f .env ]; then
            grep -E "AI_PROVIDER|OPENAI_API_KEY|ANTHROPIC_API_KEY" .env || echo "No configurado"
        else
            echo "Archivo .env no existe"
        fi
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo "💡 Para cambiar de provider:"
echo "   Ejecuta este script nuevamente o edita AI_PROVIDER en .env"
echo ""
