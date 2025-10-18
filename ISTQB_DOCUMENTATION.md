# Documentación del Sistema ISTQB para Generación de Casos de Prueba

## Descripción General

El sistema ISTQB integrado en el microservicio de análisis QA proporciona generación avanzada de casos de prueba aplicando técnicas de diseño ISTQB Foundation Level. Esta implementación combina la potencia de la IA generativa con metodologías probadas de testing.

## Características Principales

### 🎯 Técnicas ISTQB Implementadas

1. **Equivalencia**: Partición de clases de equivalencia válidas/inválidas
2. **Valores Límite**: Análisis de casos min-1, min, min+1, max-1, max, max+1
3. **Tabla de Decisión**: Matrices compactas de condiciones y acciones
4. **Transición de Estados**: Estados y transiciones principales del sistema
5. **Árbol de Clasificación**: Clases/atributos y restricciones entre factores
6. **Pairwise**: Combinaciones mínimas que cubren todas las parejas
7. **Casos de Uso**: Flujos principales y alternos relevantes
8. **Error Guessing**: Hipótesis de fallos del dominio
9. **Checklist**: Verificación genérica de calidad

### 📋 Formato de Salida Estructurado

- **Sección A**: CSV con casos de prueba (CP - NNN - PROGRAMA - MODULO - CONDICION - ESCENARIO)
- **Sección B**: Fichas detalladas con precondiciones y resultados esperados
- **Sección C**: Artefactos técnicos según técnicas seleccionadas
- **Sección D**: Plan de ejecución automatizado (opcional)

## Uso de la API

### Endpoint Principal

```http
POST /generate-istqb-tests
```

### Estructura de la Solicitud

```json
{
  "programa": "SISTEMA_AUTH",
  "dominio": "Autenticación de usuarios con validación de credenciales",
  "modulos": ["AUTORIZACION", "VALIDACION", "AUDITORIA"],
  "factores": {
    "TIPO_USUARIO": ["ADMIN", "USER", "GUEST"],
    "ESTADO_CREDENCIAL": ["VALIDA", "INVALIDA", "EXPIRADA"],
    "INTENTOS": ["OK", "ERROR_TIPO_1", "TIMEOUT"]
  },
  "limites": {
    "CAMPO_USUARIO_len": {"min": 1, "max": 64},
    "REINTENTOS": 3,
    "TIMEOUT_MS": 5000
  },
  "reglas": [
    "R1: si TIPO_USUARIO=ADMIN y ESTADO_CREDENCIAL=VALIDA -> ACCESO_TOTAL",
    "R2: si INTENTOS=TIMEOUT -> reintentar 1 vez y marcar pendiente",
    "R3: si REINTENTOS supera límite -> bloquear y auditar"
  ],
  "tecnicas": {
    "equivalencia": true,
    "valores_limite": true,
    "tabla_decision": true,
    "transicion_estados": true,
    "arbol_clasificacion": true,
    "pairwise": true,
    "casos_uso": true,
    "error_guessing": true,
    "checklist": true
  },
  "priorizacion": "Riesgo",
  "cantidad_max": 150,
  "salida_plan_ejecucion": {
    "incluir": true,
    "formato": "cursor_playwright_mcp"
  }
}
```

### Estructura de la Respuesta

```json
{
  "programa": "SISTEMA_AUTH",
  "generation_id": "istqb_SISTEMA_AUTH_1760825804",
  "status": "completed",
  "csv_cases": [
    "CP - 001 - SISTEMA_AUTH - AUTORIZACION - TIPO_USUARIO_ADMIN - AUTORIZA Y REGISTRA OPERACION",
    "CP - 002 - SISTEMA_AUTH - VALIDACION - ESTADO_CREDENCIAL_VALIDA - VALIDA Y PERMITE ACCESO"
  ],
  "fichas": [
    "1 - CP - 001 - SISTEMA_AUTH - AUTORIZACION - TIPO_USUARIO_ADMIN - AUTORIZA Y REGISTRA OPERACION\n2- Precondicion: Usuario activo; datos completos; firma válida\n3- Resultado Esperado: Operación autorizada; ID transacción generado; registro persistido y auditado"
  ],
  "artefactos_tecnicos": {
    "equivalencias": "Particiones válidas/inválidas por cada factor",
    "valores_limite": "Casos min-1,min,min+1,max-1,max,max+1 para límites",
    "tabla_decision": "Matriz Condiciones→Acciones"
  },
  "plan_ejecucion": {
    "formato": "cursor_playwright_mcp",
    "casos": []
  },
  "confidence_score": 0.85,
  "processing_time": 25.3,
  "created_at": "2025-10-18T19:16:44.520862"
}
```

## Ejemplos de Uso

### Ejemplo 1: Sistema de E-commerce

```json
{
  "programa": "ECOMMERCE_PLATFORM",
  "dominio": "Procesamiento de pedidos con validación de inventario",
  "modulos": ["INVENTARIO", "PAGOS", "ENVIO"],
  "factores": {
    "ESTADO_PRODUCTO": ["DISPONIBLE", "AGOTADO", "DESCONTINUADO"],
    "METODO_PAGO": ["TARJETA", "PAYPAL", "TRANSFERENCIA"],
    "ZONA_ENVIO": ["NACIONAL", "INTERNACIONAL", "RESTRINGIDA"]
  },
  "limites": {
    "CANTIDAD_MAX": 100,
    "MONTO_MAX": 10000,
    "TIEMPO_PROCESAMIENTO_MS": 30000
  },
  "reglas": [
    "R1: si ESTADO_PRODUCTO=DISPONIBLE y CANTIDAD<=STOCK -> PROCESAR_PEDIDO",
    "R2: si METODO_PAGO=TARJETA -> VALIDAR_TARJETA",
    "R3: si ZONA_ENVIO=RESTRINGIDA -> REQUERIR_AUTORIZACION"
  ],
  "tecnicas": {
    "equivalencia": true,
    "valores_limite": true,
    "tabla_decision": true,
    "transicion_estados": true,
    "arbol_clasificacion": false,
    "pairwise": true,
    "casos_uso": true,
    "error_guessing": true,
    "checklist": true
  },
  "priorizacion": "Riesgo",
  "cantidad_max": 100
}
```

### Ejemplo 2: Sistema de Reservas

```json
{
  "programa": "HOTEL_RESERVATIONS",
  "dominio": "Sistema de reservas de habitaciones con validación de disponibilidad",
  "modulos": ["DISPONIBILIDAD", "RESERVAS", "FACTURACION"],
  "factores": {
    "TIPO_HABITACION": ["SIMPLE", "DOBLE", "SUITE"],
    "ESTADO_RESERVA": ["PENDIENTE", "CONFIRMADA", "CANCELADA"],
    "TEMPORADA": ["ALTA", "MEDIA", "BAJA"]
  },
  "limites": {
    "ANTICIPACION_MAX_DIAS": 365,
    "ESTANCIA_MAX_DIAS": 30,
    "HABITACIONES_MAX": 10
  },
  "reglas": [
    "R1: si TIPO_HABITACION=SUITE y TEMPORADA=ALTA -> APLICAR_RECARGO",
    "R2: si ESTADO_RESERVA=PENDIENTE y ANTIGUEDAD>24h -> CANCELAR_AUTOMATICO",
    "R3: si HABITACIONES>5 -> REQUERIR_APROBACION_MANAGER"
  ],
  "tecnicas": {
    "equivalencia": true,
    "valores_limite": true,
    "tabla_decision": true,
    "transicion_estados": true,
    "arbol_clasificacion": true,
    "pairwise": true,
    "casos_uso": true,
    "error_guessing": true,
    "checklist": true
  },
  "priorizacion": "Impacto",
  "cantidad_max": 200
}
```

## Integración con Langfuse

### Observabilidad

El sistema está completamente integrado con Langfuse para proporcionar:

- **Trazabilidad completa** de cada generación de casos
- **Métricas de rendimiento** y tiempos de procesamiento
- **Análisis de calidad** de los prompts generados
- **Monitoreo de uso** de las diferentes técnicas ISTQB
- **Alertas automáticas** en caso de errores o degradación

### Metadatos Capturados

```json
{
  "trace_name": "istqb_test_generation",
  "user_id": "programa_SISTEMA_AUTH",
  "tags": ["qa", "istqb", "test_generation", "advanced_techniques"],
  "metadata": {
    "programa": "SISTEMA_AUTH",
    "generation_id": "istqb_SISTEMA_AUTH_1760825804",
    "timestamp": "2025-10-18T19:16:44.520862",
    "csv_cases_count": 45,
    "fichas_count": 45,
    "artefactos_count": 9,
    "confidence_score": 0.85
  }
}
```

## Mejores Prácticas

### 1. Definición de Factores

- **Granularidad apropiada**: Los factores deben ser atómicos y específicos
- **Valores representativos**: Incluir valores válidos, inválidos y límite
- **Cobertura completa**: Asegurar que todos los escenarios importantes estén cubiertos

### 2. Configuración de Técnicas

- **Selección estratégica**: Activar solo las técnicas relevantes para el dominio
- **Balance de cobertura**: Combinar técnicas para máxima cobertura con mínima redundancia
- **Priorización**: Usar criterios de riesgo, impacto o uso según el contexto

### 3. Límites del Sistema

- **Valores realistas**: Basar límites en restricciones reales del sistema
- **Rangos apropiados**: Definir rangos que permitan testing efectivo
- **Documentación clara**: Explicar el origen y justificación de cada límite

### 4. Reglas de Negocio

- **Claridad**: Usar sintaxis clara y consistente
- **Completitud**: Cubrir todos los escenarios de decisión importantes
- **Mantenibilidad**: Estructurar reglas de forma que sean fáciles de actualizar

## Casos de Uso Avanzados

### 1. Testing de APIs

```json
{
  "programa": "API_GATEWAY",
  "dominio": "Validación y enrutamiento de requests HTTP",
  "modulos": ["AUTHENTICATION", "RATE_LIMITING", "ROUTING"],
  "factores": {
    "HTTP_METHOD": ["GET", "POST", "PUT", "DELETE"],
    "AUTH_STATUS": ["VALID", "INVALID", "EXPIRED", "MISSING"],
    "RATE_LIMIT": ["WITHIN_LIMIT", "EXCEEDED", "BLOCKED"]
  },
  "limites": {
    "REQUEST_SIZE_MAX": 10485760,
    "RATE_LIMIT_PER_MINUTE": 100,
    "TIMEOUT_MS": 5000
  },
  "reglas": [
    "R1: si AUTH_STATUS=VALID y RATE_LIMIT=WITHIN_LIMIT -> PROCESS_REQUEST",
    "R2: si AUTH_STATUS=INVALID -> RETURN_401",
    "R3: si RATE_LIMIT=EXCEEDED -> RETURN_429"
  ],
  "tecnicas": {
    "equivalencia": true,
    "valores_limite": true,
    "tabla_decision": true,
    "transicion_estados": true,
    "arbol_clasificacion": false,
    "pairwise": true,
    "casos_uso": true,
    "error_guessing": true,
    "checklist": true
  }
}
```

### 2. Testing de Microservicios

```json
{
  "programa": "USER_SERVICE",
  "dominio": "Gestión de usuarios con validación de datos",
  "modulos": ["REGISTRATION", "PROFILE_UPDATE", "ACCOUNT_DELETION"],
  "factores": {
    "USER_STATUS": ["ACTIVE", "INACTIVE", "SUSPENDED", "PENDING"],
    "DATA_VALIDITY": ["VALID", "INVALID", "INCOMPLETE"],
    "OPERATION_TYPE": ["CREATE", "UPDATE", "DELETE", "READ"]
  },
  "limites": {
    "USERNAME_LENGTH": {"min": 3, "max": 50},
    "EMAIL_LENGTH": {"min": 5, "max": 254},
    "PROFILE_FIELDS_MAX": 20
  },
  "reglas": [
    "R1: si USER_STATUS=ACTIVE y DATA_VALIDITY=VALID -> ALLOW_OPERATION",
    "R2: si USER_STATUS=SUSPENDED -> BLOCK_OPERATION",
    "R3: si DATA_VALIDITY=INCOMPLETE y OPERATION_TYPE=CREATE -> REQUEST_COMPLETION"
  ],
  "tecnicas": {
    "equivalencia": true,
    "valores_limite": true,
    "tabla_decision": true,
    "transicion_estados": true,
    "arbol_clasificacion": true,
    "pairwise": true,
    "casos_uso": true,
    "error_guessing": true,
    "checklist": true
  }
}
```

## Monitoreo y Alertas

### Métricas Clave

- **Tiempo de procesamiento**: Tiempo promedio de generación de casos
- **Tasa de éxito**: Porcentaje de generaciones exitosas
- **Calidad de casos**: Puntuación de confianza promedio
- **Uso de técnicas**: Frecuencia de uso de cada técnica ISTQB
- **Cobertura**: Número de casos generados por módulo

### Alertas Configurables

- **Degradación de rendimiento**: Tiempo de procesamiento > 30 segundos
- **Baja calidad**: Confidence score < 0.7
- **Errores frecuentes**: Tasa de éxito < 95%
- **Uso ineficiente**: Técnicas no utilizadas consistentemente

## Troubleshooting

### Problemas Comunes

1. **Timeout en generación**
   - Verificar configuración de límites
   - Reducir cantidad_max si es necesario
   - Revisar complejidad de reglas de negocio

2. **Calidad baja de casos generados**
   - Mejorar definición de factores
   - Ajustar reglas de negocio
   - Verificar coherencia entre módulos y factores

3. **Cobertura insuficiente**
   - Activar técnicas adicionales
   - Aumentar cantidad_max
   - Revisar definición de límites

### Logs y Debugging

El sistema genera logs estructurados que incluyen:

```json
{
  "level": "info",
  "message": "ISTQB test case generation completed",
  "programa": "SISTEMA_AUTH",
  "generation_id": "istqb_SISTEMA_AUTH_1760825804",
  "csv_cases_count": 45,
  "fichas_count": 45,
  "processing_time": 25.3,
  "timestamp": "2025-10-18T19:16:44.520862"
}
```

## Conclusión

El sistema ISTQB integrado proporciona una solución robusta y escalable para la generación de casos de prueba de alta calidad. La combinación de técnicas probadas de testing con IA generativa y observabilidad completa permite a los equipos de QA:

- Generar casos de prueba más completos y sistemáticos
- Aplicar metodologías estándar de la industria
- Monitorear y mejorar continuamente el proceso
- Escalar la generación de casos de prueba de forma eficiente

Para más información o soporte, consulta la documentación de la API en `/docs` o contacta al equipo de QA.
