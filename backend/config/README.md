# Database Configuration Guide

Este directorio contiene las configuraciones de entorno para diferentes escenarios de despliegue.

## 🏗️ Configuraciones Disponibles

### 1. **Development** (`development.env`)
- **Base de datos**: SQLite (archivo local)
- **Uso**: Desarrollo local sin dependencias externas
- **Archivo**: `data/conversation_simulator.db`

### 2. **Production** (`production.env`)
- **Base de datos**: PostgreSQL
- **Uso**: Producción con base de datos dedicada
- **Configuración**: Variables individuales de PostgreSQL

### 3. **Supabase** (`supabase.env`)
- **Base de datos**: PostgreSQL (Supabase)
- **Uso**: Producción en la nube con Supabase
- **Configuración**: URL y clave de Supabase

## 🚀 Cómo Usar

### Desarrollo Local (SQLite)
```bash
# Usar configuración de desarrollo sin Docker
export ENVIRONMENT=development
export DATABASE_PATH=data/conversation_simulator.db
python scripts/setup_database.py
```

### Desarrollo con Docker (PostgreSQL)
```bash
# Usar docker-compose con PostgreSQL
docker-compose up -d postgres
docker-compose up backend
```

### Desarrollo con PostgreSQL (Docker)
```bash
# Opción 1: Usar DATABASE_URL (recomendado)
export ENVIRONMENT=development
export DATABASE_URL=postgresql://postgres:postgres@postgres:5432/conversation_simulator

# Opción 2: Variables individuales
export ENVIRONMENT=development
export POSTGRES_HOST=postgres
export POSTGRES_DB=conversation_simulator
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres

# Inicializar base de datos
python scripts/setup_database.py
```

### Producción con PostgreSQL
```bash
# Usar configuración de producción
export ENVIRONMENT=production
python scripts/setup_database.py
```

### Producción con Supabase
```bash
# Usar configuración de Supabase
export ENVIRONMENT=supabase
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_ANON_KEY=your-anon-key

python scripts/setup_database.py
```

## 🔄 Migración de Datos

### De SQLite a PostgreSQL
```bash
# 1. Configurar PostgreSQL
export ENVIRONMENT=production
export POSTGRES_HOST=localhost
export POSTGRES_DB=conversation_simulator
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password

# 2. Migrar datos
python scripts/migrate_to_postgres.py
```

## 🐳 Docker

### Desarrollo con Docker
```bash
# Usar docker-compose con PostgreSQL
docker-compose up -d postgres
docker-compose up backend
```

### Producción con Docker
```bash
# Usar variables de entorno de producción
docker-compose -f docker-compose.production.yml up
```

## 📊 Jerarquía de Configuración

El sistema sigue esta jerarquía de configuración:

1. **Variables de entorno del sistema** (más alta prioridad)
2. **Archivo de configuración del entorno** (`{ENVIRONMENT}.env`)
3. **Valores por defecto** (más baja prioridad)

## 🔧 Variables de Entorno

### PostgreSQL
- `POSTGRES_HOST`: Host de PostgreSQL
- `POSTGRES_PORT`: Puerto (default: 5432)
- `POSTGRES_DB`: Nombre de la base de datos
- `POSTGRES_USER`: Usuario
- `POSTGRES_PASSWORD`: Contraseña

### Supabase
- `SUPABASE_URL`: URL del proyecto Supabase
- `SUPABASE_ANON_KEY`: Clave anónima de Supabase

### SQLite (Fallback)
- `DATABASE_PATH`: Ruta del archivo SQLite

### Configuración Directa
- `DATABASE_URL`: URL completa de la base de datos (sobrescribe todo)

## 🚨 Notas Importantes

1. **SQLite es solo para desarrollo**: No usar en producción
2. **PostgreSQL es preferido**: Para desarrollo y producción
3. **Supabase es para nube**: Para despliegues en la nube
4. **Migración automática**: El sistema migra automáticamente de SQLite a PostgreSQL cuando está disponible
5. **Fallback inteligente**: Si PostgreSQL no está disponible, usa SQLite automáticamente