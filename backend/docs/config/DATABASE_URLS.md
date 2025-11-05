# Database URLs Configuration Guide

## 🐳 Docker Development (Recomendado)

### Para desarrollo con Docker Compose:
```bash
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/conversation_simulator
```

**Componentes:**
- **Usuario**: `postgres`
- **Contraseña**: `postgres`
- **Host**: `postgres` (nombre del servicio en Docker)
- **Puerto**: `5432`
- **Base de datos**: `conversation_simulator`

## 🏠 Desarrollo Local (Sin Docker)

### Para desarrollo local con PostgreSQL:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/conversation_simulator
```

**Componentes:**
- **Usuario**: `postgres`
- **Contraseña**: `postgres`
- **Host**: `localhost`
- **Puerto**: `5432`
- **Base de datos**: `conversation_simulator`

## 🚀 Producción

### Para producción con PostgreSQL:
```bash
DATABASE_URL=postgresql://conversation_user:secure_password@production-host:5432/conversation_simulator
```

**Componentes:**
- **Usuario**: `conversation_user` (usuario específico de la aplicación)
- **Contraseña**: `secure_password` (contraseña segura)
- **Host**: `production-host` (host de producción)
- **Puerto**: `5432`
- **Base de datos**: `conversation_simulator`

## ☁️ Supabase (Cloud)

### Para producción en la nube con Supabase:
```bash
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
```

**Componentes:**
- **Usuario**: `postgres`
- **Contraseña**: `[password]` (contraseña del proyecto Supabase)
- **Host**: `db.[project-id].supabase.co`
- **Puerto**: `5432`
- **Base de datos**: `postgres`

## 🔧 Configuraciones por Entorno

### 1. Development (Docker)
```bash
# backend/config/development.env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/conversation_simulator
```

### 2. Production
```bash
# backend/config/production.env
DATABASE_URL=postgresql://conversation_user:secure_password@production-host:5432/conversation_simulator
```

### 3. Supabase
```bash
# backend/config/supabase.env
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
```

### 4. Docker
```bash
# backend/config/docker.env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/conversation_simulator
```

## 🧪 Pruebas de Configuración

### Probar configuración Docker:
```bash
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/conversation_simulator python scripts/test_docker_config.py
```

### Probar configuración general:
```bash
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/conversation_simulator python scripts/simple_config_test.py
```

## 📝 Notas Importantes

1. **Docker**: El host debe ser `postgres` (nombre del servicio)
2. **Local**: El host debe ser `localhost`
3. **Producción**: Usar credenciales seguras y host real
4. **Supabase**: Usar la URL específica del proyecto
5. **Fallback**: Si no hay DATABASE_URL, usa variables individuales o SQLite

## 🔄 Migración

### De SQLite a PostgreSQL:
```bash
# 1. Configurar PostgreSQL
export DATABASE_URL=postgresql://postgres:postgres@postgres:5432/conversation_simulator

# 2. Migrar datos
python scripts/migrate_to_postgres.py
```

### De archivos JSON a PostgreSQL:
```bash
# 1. Configurar PostgreSQL
export DATABASE_URL=postgresql://postgres:postgres@postgres:5432/conversation_simulator

# 2. Inicializar base de datos
python scripts/setup_database.py

# 3. Migrar datos
python scripts/migrate_to_postgres.py
```
