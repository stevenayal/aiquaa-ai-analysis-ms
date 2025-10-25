# Colecciones de Postman para API Análisis QA

Este directorio contiene diferentes versiones de colecciones de Postman para la API de Análisis QA, cada una con diferentes niveles de funcionalidad y compatibilidad.

## 📁 Archivos Disponibles

### 1. `postman_collection_simple.json` - **RECOMENDADO PARA INICIAR**
- **Descripción**: Colección básica sin pruebas automáticas
- **Uso**: Ideal para pruebas manuales y exploración de la API
- **Características**:
  - ✅ 8 endpoints principales
  - ✅ URL de producción configurada
  - ✅ Parámetros en español
  - ✅ Sin dependencias de environments
  - ✅ Compatible con todas las versiones de Postman

### 2. `postman_collection_con_pruebas.json` - **RECOMENDADO PARA TESTING**
- **Descripción**: Colección con pruebas automáticas completas
- **Uso**: Ideal para testing automatizado y validación de la API
- **Características**:
  - ✅ 8 endpoints principales
  - ✅ Pruebas automáticas para cada endpoint
  - ✅ Validación de estructura de respuesta
  - ✅ Verificación de tiempos de respuesta
  - ✅ Pruebas de validación (errores 422)
  - ✅ URL de producción configurada

### 3. `postman_collection_corregida.json` - **VERSIÓN COMPLETA**
- **Descripción**: Colección completa con todas las funcionalidades
- **Uso**: Para usuarios avanzados que necesitan todas las funcionalidades
- **Características**:
  - ✅ 16 requests en total
  - ✅ Pruebas automáticas completas
  - ✅ Scripts globales
  - ✅ Variables de entorno
  - ✅ Validaciones exhaustivas

## 🚀 Cómo Usar las Colecciones

### Importar en Postman

1. **Abrir Postman**
2. **Hacer clic en "Import"**
3. **Seleccionar el archivo JSON deseado**
4. **La colección se importará automáticamente**

### Configuración

- **URL Base**: Ya configurada como `https://ia-analisis-production.up.railway.app`
- **Variables**: No se requieren configuraciones adicionales
- **Environments**: No necesarios

### Ejecutar Pruebas

#### Para Colección Simple:
1. Seleccionar cualquier request
2. Hacer clic en "Send"
3. Ver la respuesta

#### Para Colecciones con Pruebas:
1. Hacer clic derecho en la colección
2. Seleccionar "Run collection"
3. Ver los resultados de las pruebas

## 📊 Endpoints Disponibles

### Endpoints Principales
- **`GET /salud`** - Health Check
- **`POST /analizar`** - Análisis de Contenido
- **`POST /analizar-jira`** - Análisis de Jira
- **`POST /generar-pruebas-avanzadas`** - Generación Avanzada
- **`POST /analisis/requisitos/verificacion-istqb`** - Análisis ISTQB
- **`POST /analizar-jira-confluence`** - Análisis Jira-Confluence

### Endpoints de Validación
- **Validación de errores 422** - Pruebas de validación

## 🧪 Tipos de Pruebas Incluidas

### Pruebas de Éxito (200)
- ✅ **Status Code**: Verificación de código 200
- ✅ **Campos Requeridos**: Validación de estructura de respuesta
- ✅ **Tipos de Datos**: Verificación de tipos correctos
- ✅ **Valores Válidos**: Rangos y formatos esperados
- ✅ **Tiempo de Respuesta**: Límites de performance

### Pruebas de Validación (422)
- ✅ **Status Code**: Verificación de código 422
- ✅ **Mensajes de Error**: Estructura de errores de validación
- ✅ **Tiempo de Respuesta**: Respuestas rápidas para errores

## 🔧 Solución de Problemas

### Error: "Collection not compatible"
- **Solución**: Usar `postman_collection_simple.json`
- **Causa**: Versión de Postman muy antigua

### Error: "Tests not running"
- **Solución**: Verificar que estás usando una versión reciente de Postman
- **Causa**: Versiones antiguas no soportan todas las funciones de testing

### Error: "Variable not found"
- **Solución**: La variable `base_url` está configurada en la colección
- **Causa**: No se requiere configuración adicional

## 📈 Estadísticas de las Colecciones

| Colección | Requests | Pruebas | Compatibilidad | Uso Recomendado |
|-----------|----------|---------|----------------|-----------------|
| Simple | 8 | 0 | Alta | Exploración |
| Con Pruebas | 8 | 40+ | Media | Testing |
| Completa | 16 | 80+ | Baja | Avanzado |

## 🎯 Recomendaciones de Uso

### Para Desarrolladores
- **Inicio**: Usar `postman_collection_simple.json`
- **Testing**: Migrar a `postman_collection_con_pruebas.json`
- **Avanzado**: Usar `postman_collection_corregida.json`

### Para QA
- **Recomendado**: `postman_collection_con_pruebas.json`
- **Beneficio**: Pruebas automáticas completas

### Para Product Managers
- **Recomendado**: `postman_collection_simple.json`
- **Beneficio**: Fácil exploración de la API

## 🔄 Actualizaciones

- **Versión 1.0**: Colección simple
- **Versión 2.0**: Colección con pruebas
- **Versión 3.0**: Colección completa

## 📞 Soporte

Si tienes problemas con las colecciones:
1. Verificar que estás usando Postman v8.0+
2. Probar con la colección simple primero
3. Verificar que la URL de producción esté funcionando

---

**¡Las colecciones están listas para usar en producción!** 🚀
