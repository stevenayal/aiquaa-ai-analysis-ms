# Security Policy

## Supported Versions

Estas son las series que reciben **actualizaciones de seguridad**. Las series marcadas con ❌ están en fin de vida (EOL).

| Versión | Estado              | Fin de soporte |
|--------:|---------------------|----------------|
| 1.3.x   | ✅ Activa            | 2026-03-31     |
| 1.2.x   | ✅ Solo parches críticos | 2025-12-31     |
| < 1.2   | ❌ EOL               | —              |

> Usamos SemVer. `1.3.x` abarca todos los parches de la rama menor 1.3.

---

## Reporting a Vulnerability

**Por favor no abras issues públicos para vulnerabilidades.**
En su lugar, elegí uno de estos canales privados:

- **Email:** admin@aiquaa.com   
- **GitHub Security Advisory:** _Security → Report a vulnerability_ en este repositorio.

### Qué incluir
- Versión afectada, entorno, y pasos reproducibles mínimos.  
- Impacto esperado (lectura/escalado/ejecución), severidad estimada (CVSS si es posible).  
- PoC **no destructivo** (sin exfiltrar datos reales).

### Niveles de servicio (SLA)
- **Acuse de recibo:** dentro de **72 h**.  
- **Triage inicial:** dentro de **7 días** (confirmación del alcance/severidad).  
- **Parche/mitigación:** meta de **30 días** para alta/critica (puede variar por complejidad).  
- Te mantendremos actualizado al menos **semanalmente** hasta el cierre.

### Coordinated Disclosure
- Preferimos divulgación coordinada. Acordaremos una fecha de publicación tras disponer de parche/mitigación.  
- Agradecemos y, si lo deseás, **damos crédito** en el changelog/advisory.  
- Gestionamos **CVE** a través de GitHub Advisories cuando corresponda.

### Alcance
- Código y configuraciones de este repo, imágenes y ejemplo de despliegue.  
- **Fuera de alcance:** ingeniería social, cuentas personales, servicios de terceros fuera de nuestro control, denegación de servicio puramente volumétrica.

### Safe Harbor
La investigación realizada de **buena fe** siguiendo esta política **no será objeto de acciones legales** por nuestra parte. Evitá afectar a otros usuarios o comprometer datos reales.

---

## Contacto de emergencia
Para incidencias activas en producción que afecten a usuarios: **security@aiquaa.com** con asunto `[URGENTE]`.
