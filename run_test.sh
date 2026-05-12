#!/bin/bash

echo "🧪 Verificando dependencias..."

# Instalar dependencias necesarias

echo "📦 Instalando dependencias de testing..."
pip install pytest pytest-django pytest-cov pytest-asyncio pytest-mock -q

echo ""
echo "🧪 Ejecutando tests sin coverage primero..."

# Primero sin coverage
pytest tests/ -v --tb=short --disable-warnings

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests exitosos. Ejecutando con coverage..."
    echo ""
    
    # Luego con coverage
    pytest tests/ \
        -v \
        --cov=apps \
        --cov=core \
        --cov=config \
        --cov-report=term-missing \
        --cov-report=html \
        --tb=short \
        --disable-warnings \
        --no-cov-on-fail
    
    echo ""
    echo "📊 Reporte HTML generado en htmlcov/index.html"
else
    echo ""
    echo "❌ Tests fallaron. Revisa los errores antes de ejecutar coverage."
    exit 1
fi