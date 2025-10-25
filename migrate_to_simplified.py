"""
Script de Migración a Versión Simplificada
Ayuda a migrar desde la versión anterior a la nueva estructura
"""

import os
import shutil
from datetime import datetime

def backup_original_files():
    """Crear backup de archivos originales"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "main.py",
        "postman_collection_simple.json",
        "postman_collection_con_pruebas.json",
        "postman_collection_corregida.json"
    ]
    
    print(f"📁 Creando backup en {backup_dir}/")
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"   ✅ {file} -> {backup_dir}/{file}")
        else:
            print(f"   ⚠️  {file} no encontrado")
    
    return backup_dir

def create_env_file():
    """Crear archivo .env con configuración por defecto"""
    env_content = """# Feature Flags
USE_SPANISH_PARAMS=false

# Jira Configuration
JIRA_URL=https://your-jira-instance.atlassian.net
JIRA_USERNAME=your-username
JIRA_API_TOKEN=your-api-token

# LLM Configuration
GOOGLE_API_KEY=your-google-api-key
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://your-langfuse-instance.com
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ Archivo .env creado con configuración por defecto")

def update_requirements():
    """Verificar que requirements.txt esté actualizado"""
    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt encontrado")
    else:
        print("⚠️  requirements.txt no encontrado - crear manualmente")

def create_startup_script():
    """Crear script de inicio para la versión simplificada"""
    startup_content = """#!/bin/bash
# Script de inicio para versión simplificada

echo "🚀 Iniciando Microservicio de Análisis QA - Versión Simplificada"
echo "📊 Feature Flag: USE_SPANISH_PARAMS=${USE_SPANISH_PARAMS:-false}"

# Verificar variables de entorno
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ GOOGLE_API_KEY no configurada"
    exit 1
fi

if [ -z "$LANGFUSE_PUBLIC_KEY" ]; then
    echo "❌ LANGFUSE_PUBLIC_KEY no configurada"
    exit 1
fi

# Iniciar aplicación
echo "✅ Iniciando aplicación..."
python main_simplified.py
"""
    
    with open("start_simplified.sh", "w", encoding="utf-8") as f:
        f.write(startup_content)
    
    # Hacer ejecutable en sistemas Unix
    if os.name != 'nt':  # No Windows
        os.chmod("start_simplified.sh", 0o755)
    
    print("✅ Script de inicio creado: start_simplified.sh")

def create_docker_compose_simplified():
    """Crear docker-compose para versión simplificada"""
    docker_compose_content = """version: '3.8'

services:
  ia-analisis-simplified:
    build: .
    ports:
      - "8000:8000"
    environment:
      - USE_SPANISH_PARAMS=false
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_HOST=${LANGFUSE_HOST}
      - JIRA_URL=${JIRA_URL}
      - JIRA_USERNAME=${JIRA_USERNAME}
      - JIRA_API_TOKEN=${JIRA_API_TOKEN}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/salud"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
    
    with open("docker-compose-simplified.yml", "w", encoding="utf-8") as f:
        f.write(docker_compose_content)
    
    print("✅ Docker Compose simplificado creado: docker-compose-simplified.yml")

def create_test_script():
    """Crear script de prueba automatizado"""
    test_script_content = """#!/bin/bash
# Script de prueba automatizado

echo "🧪 Ejecutando pruebas del microservicio simplificado..."

# Verificar que el servicio esté ejecutándose
echo "📡 Verificando conectividad..."
if curl -f http://localhost:8000/salud > /dev/null 2>&1; then
    echo "✅ Servicio ejecutándose"
else
    echo "❌ Servicio no disponible - iniciar primero"
    exit 1
fi

# Ejecutar pruebas
echo "🚀 Ejecutando pruebas..."
python test_simplified.py

echo "🏁 Pruebas completadas"
"""
    
    with open("test_automated.sh", "w", encoding="utf-8") as f:
        f.write(test_script_content)
    
    # Hacer ejecutable en sistemas Unix
    if os.name != 'nt':  # No Windows
        os.chmod("test_automated.sh", 0o755)
    
    print("✅ Script de prueba automatizado creado: test_automated.sh")

def main():
    """Función principal de migración"""
    print("🔄 Iniciando migración a versión simplificada...")
    print("=" * 60)
    
    # 1. Crear backup
    backup_dir = backup_original_files()
    
    # 2. Crear archivo .env
    create_env_file()
    
    # 3. Verificar requirements
    update_requirements()
    
    # 4. Crear script de inicio
    create_startup_script()
    
    # 5. Crear docker-compose
    create_docker_compose_simplified()
    
    # 6. Crear script de prueba
    create_test_script()
    
    print("\n" + "=" * 60)
    print("✅ Migración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Configurar variables de entorno en .env")
    print("2. Ejecutar: python main_simplified.py")
    print("3. Probar: python test_simplified.py")
    print("4. Usar colecciones de Postman actualizadas")
    print(f"\n📁 Backup creado en: {backup_dir}/")
    print("\n🚀 ¡Listo para usar la versión simplificada!")

if __name__ == "__main__":
    main()
