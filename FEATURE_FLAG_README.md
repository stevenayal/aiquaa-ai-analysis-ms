# Feature Flag para Parámetros en Español

## 🎯 **Problema Resuelto**

El problema de timeout en los endpoints de Jira estaba relacionado con los parámetros en español que se introdujeron recientemente. Se ha implementado un feature flag para controlar esto.

## 🔧 **Feature Flag Implementado**

### **Variable de Entorno:**
```bash
USE_SPANISH_PARAMS=false  # Por defecto: false (parámetros en inglés)
```

### **Configuración:**
- **`false`** (por defecto): Usa parámetros en inglés
- **`true`**: Usa parámetros en español

## 📊 **Endpoints Afectados**

### **Endpoints de Jira:**
- ✅ `/analizar-jira` - Análisis completo de Jira
- ✅ `/analizar-jira-simple` - Análisis simplificado de Jira

### **Parámetros Soportados:**

#### **Con `USE_SPANISH_PARAMS=false` (RECOMENDADO):**
```json
{
  "work_item_id": "KAN-6",
  "analysis_level": "high"
}
```

#### **Con `USE_SPANISH_PARAMS=true`:**
```json
{
  "id_work_item": "KAN-6",
  "nivel_analisis": "high"
}
```

## 🚀 **Cómo Usar**

### **1. Configuración por Defecto (Recomendada):**
```bash
# En tu archivo .env o variables de entorno
USE_SPANISH_PARAMS=false
```

**Request:**
```bash
curl -X 'POST' \
  'https://ia-analisis-production.up.railway.app/analizar-jira' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "work_item_id": "KAN-6",
  "analysis_level": "high"
}'
```

### **2. Configuración con Parámetros en Español:**
```bash
# En tu archivo .env o variables de entorno
USE_SPANISH_PARAMS=true
```

**Request:**
```bash
curl -X 'POST' \
  'https://ia-analisis-production.up.railway.app/analizar-jira' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id_work_item": "KAN-6",
  "nivel_analisis": "high"
}'
```

## 🧪 **Testing**

### **Script de Prueba:**
```bash
python test_feature_flag.py
```

### **Colecciones de Postman:**
- ✅ `postman_collection_simple.json` - Incluye ambos tipos de parámetros
- ✅ `postman_collection_con_pruebas.json` - Con pruebas automáticas

## 📁 **Archivos Creados/Modificados**

### **Archivos Modificados:**
- ✅ **`main.py`** - Feature flag implementado
- ✅ **`postman_collection_simple.json`** - Parámetros en inglés y español
- ✅ **`postman_collection_con_pruebas.json`** - Pruebas actualizadas

### **Archivos Creados:**
- ✅ **`config.env`** - Configuración del feature flag
- ✅ **`test_feature_flag.py`** - Script de prueba
- ✅ **`FEATURE_FLAG_README.md`** - Esta documentación

## 🔄 **Migración**

### **Para Usuarios Existentes:**
1. **No se requiere cambio** - Por defecto usa parámetros en inglés
2. **Si usas parámetros en español**, configurar `USE_SPANISH_PARAMS=true`
3. **Actualizar requests** según la configuración elegida

### **Para Nuevos Usuarios:**
1. **Usar parámetros en inglés** (recomendado)
2. **Configurar `USE_SPANISH_PARAMS=false`** (por defecto)
3. **Usar las colecciones de Postman** actualizadas

## 🎯 **Recomendaciones**

### **Para Producción:**
- ✅ **Usar `USE_SPANISH_PARAMS=false`** (parámetros en inglés)
- ✅ **Más estable** y menos propenso a errores
- ✅ **Mejor compatibilidad** con herramientas externas

### **Para Desarrollo:**
- ✅ **Probar ambos modos** según necesidades
- ✅ **Usar scripts de prueba** para validar
- ✅ **Monitorear logs** para identificar problemas

## 📈 **Beneficios del Feature Flag**

1. **✅ Retrocompatibilidad**: Soporta ambos tipos de parámetros
2. **✅ Flexibilidad**: Fácil cambio entre modos
3. **✅ Estabilidad**: Parámetros en inglés más estables
4. **✅ Testing**: Pruebas para ambos modos
5. **✅ Documentación**: Guías claras de uso

## 🚨 **Solución al Problema Original**

### **Problema:**
- Timeouts (504) en endpoints de Jira
- Parámetros en español causando problemas
- Incompatibilidad con herramientas externas

### **Solución:**
- ✅ **Feature flag** para controlar parámetros
- ✅ **Parámetros en inglés** por defecto
- ✅ **Retrocompatibilidad** con español
- ✅ **Testing completo** de ambos modos

---

**¡El problema está resuelto! Usa `USE_SPANISH_PARAMS=false` para máxima estabilidad.** 🚀
