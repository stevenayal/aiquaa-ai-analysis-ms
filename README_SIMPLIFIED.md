# Microservicio de Análisis QA - Versión Limpia

## 🎯 **Estructura Limpia y Optimizada**

El código ha sido refactorizado y limpiado para eliminar duplicación, archivos redundantes y crear una estructura optimizada.

### 📁 **Archivos Principales (25 archivos esenciales):**

#### **`main_simplified.py`** - Aplicación Principal
- ✅ **FastAPI app** simplificada
- ✅ **Feature flag** para parámetros en inglés/español
- ✅ **Endpoints** que usan funciones de otros archivos
- ✅ **Sin duplicación** de clases

#### **`jira_endpoints.py`** - Endpoints de Jira
- ✅ **`JiraAnalysisRequest`** - Modelo unificado
- ✅ **`analyze_jira_workitem()`** - Análisis completo
- ✅ **`analyze_jira_workitem_simple()`** - Análisis simplificado
- ✅ **Soporte** para parámetros en inglés y español

#### **`confluence_endpoints.py`** - Endpoints de Confluence
- ✅ **`ConfluenceTestPlanRequest`** - Modelo unificado
- ✅ **`analyze_jira_confluence()`** - Análisis completo
- ✅ **`analyze_jira_confluence_simple()`** - Análisis simplificado
- ✅ **Soporte** para parámetros en inglés y español

#### **`basic_endpoints.py`** - Endpoints Básicos
- ✅ **`AnalysisRequest`** - Modelo unificado
- ✅ **`analyze_content()`** - Análisis de contenido
- ✅ **`generate_advanced_tests()`** - Generación avanzada
- ✅ **Soporte** para parámetros en inglés y español

#### **`feature_flag_config.py`** - Configuración
- ✅ **Feature flags** centralizados
- ✅ **Mapeo de parámetros** dinámico
- ✅ **Configuración** unificada

#### **Módulos Core:**
- ✅ **`tracker_client.py`** - Cliente de Jira
- ✅ **`llm_wrapper.py`** - Wrapper de LLM
- ✅ **`prompt_templates.py`** - Plantillas de prompts
- ✅ **`sanitizer.py`** - Sanitización de datos

#### **Testing:**
- ✅ **`test_simplified.py`** - Script de prueba principal
- ✅ **`tests/`** - Tests unitarios

#### **Colecciones de Postman:**
- ✅ **`postman_collection_simple.json`** - Colección simple
- ✅ **`postman_collection_con_pruebas.json`** - Colección con pruebas

### 🔧 **Feature Flag:**

```bash
USE_SPANISH_PARAMS=false  # Por defecto: parámetros en inglés
USE_SPANISH_PARAMS=true   # Parámetros en español
```

### 📊 **Endpoints Disponibles:**

#### **Sistema:**
- ✅ **`GET /salud`** - Estado del servicio
- ✅ **`GET /diagnostico-llm`** - Diagnóstico LLM

#### **Análisis Básico:**
- ✅ **`POST /analizar`** - Análisis de contenido

#### **Integración Jira:**
- ✅ **`POST /analizar-jira`** - Análisis completo
- ✅ **`POST /analizar-jira-simple`** - Análisis simplificado

#### **Integración Confluence:**
- ✅ **`POST /analizar-jira-confluence`** - Análisis completo
- ✅ **`POST /analizar-jira-confluence-simple`** - Análisis simplificado

#### **Generación Avanzada:**
- ✅ **`POST /generar-pruebas-avanzadas`** - Casos de prueba avanzados

### 🧪 **Testing:**

#### **Script de Prueba:**
```bash
python test_simplified.py
```

#### **Colecciones de Postman:**
- ✅ **`postman_collection_simple.json`** - Parámetros en inglés y español
- ✅ **`postman_collection_con_pruebas.json`** - Con pruebas automáticas

### 🚀 **Cómo Usar:**

#### **1. Configuración por Defecto (Recomendada):**
```bash
# En tu archivo .env
USE_SPANISH_PARAMS=false
```

**Request con parámetros en inglés:**
```bash
curl -X 'POST' \
  'https://ia-analisis-production.up.railway.app/analizar-jira' \
  -H 'Content-Type: application/json' \
  -d '{
  "work_item_id": "KAN-6",
  "analysis_level": "high"
}'
```

#### **2. Configuración con Parámetros en Español:**
```bash
# En tu archivo .env
USE_SPANISH_PARAMS=true
```

**Request con parámetros en español:**
```bash
curl -X 'POST' \
  'https://ia-analisis-production.up.railway.app/analizar-jira' \
  -H 'Content-Type: application/json' \
  -d '{
  "id_work_item": "KAN-6",
  "nivel_analisis": "high"
}'
```

### 📈 **Beneficios de la Refactorización y Limpieza:**

1. **✅ Sin Duplicación**: Clases unificadas que soportan ambos tipos de parámetros
2. **✅ Separación de Responsabilidades**: Un archivo por funcionalidad
3. **✅ Mantenibilidad**: Código más limpio y fácil de mantener
4. **✅ Reutilización**: Funciones reutilizables entre endpoints
5. **✅ Testing**: Scripts de prueba simplificados
6. **✅ Feature Flag**: Control dinámico de parámetros
7. **✅ Estructura Limpia**: Eliminados 25+ archivos redundantes
8. **✅ Documentación Unificada**: Una sola fuente de verdad
9. **✅ Colecciones Optimizadas**: Solo las necesarias
10. **✅ Navegación Simplificada**: Estructura clara y organizada

### 🔄 **Migración desde Versión Anterior:**

#### **Para Desarrolladores:**
1. **Usar `main_simplified.py`** en lugar de `main.py`
2. **Importar funciones** desde archivos específicos
3. **Configurar feature flag** según necesidades
4. **Usar scripts de prueba** actualizados

#### **Para Usuarios:**
1. **No se requiere cambio** - API compatible
2. **Usar parámetros en inglés** (recomendado)
3. **Configurar `USE_SPANISH_PARAMS=false`** (por defecto)
4. **Usar colecciones de Postman** actualizadas

### 🎯 **Recomendaciones:**

#### **Para Producción:**
- ✅ **Usar `USE_SPANISH_PARAMS=false`** (parámetros en inglés)
- ✅ **Más estable** y menos propenso a errores
- ✅ **Mejor compatibilidad** con herramientas externas

#### **Para Desarrollo:**
- ✅ **Probar ambos modos** según necesidades
- ✅ **Usar scripts de prueba** para validar
- ✅ **Monitorear logs** para identificar problemas

---

**¡Código simplificado y sin duplicación!** 🚀
