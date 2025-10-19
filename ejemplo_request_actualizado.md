# Ejemplo de Request Body Actualizado

## ✅ **Request Body con Módulo y Servicio Publicado**

### Ejemplo Completo:

```json
{
  "requerimiento": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
  "aplicacion": "SISTEMA_AUTH",
  "modulo": "AUTENTICACION",
  "servicio_publicado": "https://auth.sistema.com/login"
}
```

### Ejemplo sin Servicio Publicado:

```json
{
  "requerimiento": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
  "aplicacion": "SISTEMA_AUTH",
  "modulo": "AUTENTICACION"
}
```

## 📋 **Campos del Request Body:**

| Campo | Tipo | Requerido | Descripción | Ejemplo |
|-------|------|-----------|-------------|---------|
| `requerimiento` | string | ✅ | Requerimiento completo a analizar | "El sistema debe permitir..." |
| `aplicacion` | string | ✅ | Nombre de la aplicación o sistema | "SISTEMA_AUTH" |
| `modulo` | string | ✅ | Módulo específico del sistema que se va a probar | "AUTENTICACION" |
| `servicio_publicado` | string | ❌ | URL o nombre del servicio publicado | "https://auth.sistema.com/login" |

## 🎯 **Estructura de Casos de Prueba Generados:**

### Con Servicio Publicado:
```json
{
  "test_case_id": "CP-001-SISTEMA_AUTH-AUTENTICACION-DATO-CONDICION-RESULTADO",
  "title": "CP - 001 - SISTEMA_AUTH - AUTENTICACION - DATO - CONDICION - RESULTADO",
  "preconditions": [
    "Precondicion: Ingresar al publicado https://auth.sistema.com/login",
    "Precondicion: Usuario existe en la base de datos",
    "Precondicion: Sistema de autenticación activo"
  ],
  "expected_result": "Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard"
}
```

### Sin Servicio Publicado:
```json
{
  "test_case_id": "CP-001-SISTEMA_AUTH-AUTENTICACION-DATO-CONDICION-RESULTADO",
  "title": "CP - 001 - SISTEMA_AUTH - AUTENTICACION - DATO - CONDICION - RESULTADO",
  "preconditions": [
    "Precondicion: Usuario existe en la base de datos",
    "Precondicion: Sistema de autenticación activo"
  ],
  "expected_result": "Resultado Esperado: Usuario autenticado exitosamente y redirigido al dashboard"
}
```

## 🔧 **Lógica de Generación:**

1. **ID y Título**: Se generan automáticamente usando `aplicacion` y `modulo`
2. **Precondiciones**: Si se proporciona `servicio_publicado`, se agrega como primera precondición
3. **Numeración**: Los casos se numeran secuencialmente (001, 002, 003, etc.)
4. **Estructura**: Se mantiene el formato `CP - 001 - APLICACION - MODULO - DATO - CONDICION - RESULTADO`

## 🚀 **Uso del Endpoint:**

```bash
curl -X POST "http://localhost:8000/generate-advanced-tests" \
  -H "Content-Type: application/json" \
  -d '{
    "requerimiento": "El sistema debe permitir a los usuarios autenticarse usando email y contraseña. El sistema debe validar las credenciales contra la base de datos y permitir el acceso solo a usuarios activos. En caso de credenciales incorrectas, debe mostrar un mensaje de error apropiado.",
    "aplicacion": "SISTEMA_AUTH",
    "modulo": "AUTENTICACION",
    "servicio_publicado": "https://auth.sistema.com/login"
  }'
```

## 📊 **Beneficios de la Actualización:**

1. **Módulo Específico**: Los casos de prueba se generan para el módulo específico
2. **Servicio Publicado**: Se incluye la URL del servicio en las precondiciones
3. **Estructura Consistente**: Formato estandarizado en todos los casos
4. **Flexibilidad**: El servicio publicado es opcional
5. **Trazabilidad**: Fácil identificación del contexto de cada caso de prueba
