# 🤖 AGENT_CONTEXT: GLPI MCP Server

Si eres un modelo de IA interactuando con este proyecto, usa este documento para entender rápidamente tu entorno, tus herramientas y el contexto operativo.

## 📝 Resumen del Proyecto
El **GLPI MCP Server** es un puente (Primary Adapter) que permite a las IAs gestionar una instancia de **GLPI (ITSM)** a través del protocolo MCP. 
Este servidor funciona conjuntamente con un cliente complementario, el **mcp-client**, que interactúa con esta interfaz para orquestar las operaciones.

Su función principal es automatizar la creación de contratos, tickets y facturas mediante el procesamiento inteligente de documentos (PDF, etc.) usando LLMs locales o remotos.

## 🏗️ Arquitectura y Estándares
- **Arquitectura Hexagonal (Puertos y Adaptadores)**: 
    - El **Dominio** define la lógica de negocio y modelos (`src/glpi_mcp_server/glpi/models.py`).
    - Los **Adaptadores Primarios** son las herramientas en `tools/`.
    - Los **Adaptadores Secundarios** son el cliente de la API de GLPI y los procesadores LLM.
- **SOLID**: El código sigue estos principios para ser altamente modular y extensible.
- **Seguridad**: Solo se puede acceder a archivos dentro de las rutas definidas en `ALLOWED_ROOTS` (en el archivo `.env`).

## 🛠️ Herramientas Disponibles (Tools)
Como agente, tienes acceso a varios módulos de herramientas:
1.  **Gestión de Contratos (`contract_tools`)**: Buscar, crear, actualizar y borrar contratos. Permite adjuntar archivos directamente.
2.  **Gestión de Tickets (`ticket_tools`)**: Operaciones CRUD sobre tickets de GLPI.
3.  **Gestión de Facturas (`invoice_tools`)**: Gestión básica de facturas/presupuestos.
4.  **Procesamiento de Documentos (`document_tools`)**: `process_contract` y `process_invoice`. Estas herramientas extraen datos estructurados de un archivo usando un LLM subordinado.
5.  **Procesamiento por Lotes (`batch_tools`)**: `tool_batch_contracts`. Procesa múltiples archivos de una carpeta de una sola vez.
6.  **Exploración de Archivos (`folder_tools`)**: Listar carpetas y verificar acceso de lectura.

## 📁 Manejo de Rutas (Hosts vs. Docker)
**IMPORTANTE**: Si detectas que el servidor corre en Docker (revisando logs o rutas internas `/app/data/`), debes saber que existe un mapeo de rutas. 
- Debes informar al usuario de las rutas del **Host** (p. ej. `/home/gokushan/...`).
- El servidor traducirá internamente estas rutas a las del contenedor para realizar las operaciones de archivo.
- No intentes adivinar rutas del sistema operativo si no están en `ALLOWED_ROOTS`.

## ⚠️ Manejo de Errores (Protocolo)
Las herramientas retornan códigos de error estandarizados:
- **100**: Error de lectura o archivo malformado.
- **101**: Posible intento de **Prompt Injection** detectado en el archivo.
- **102**: Extensión de archivo no permitida.
- **103**: Acceso denegado (fuera de `ALLOWED_ROOTS`).
- **104**: Ruta no encontrada.
- **105**: Timeout del LLM o sesión cancelada (Ollama no responde o tarda demasiado).

## 📚 Documentación de Referencia
Para más detalles específicos, consulta los documentos en la carpeta `/docs`:
- `architecture.md`: Diagramas y flujo de ejecución.
- `CONTRACT_TOOLS.md`: Detalle exhaustivo de las herramientas de contratos.
- `DEPLOYMENT.md`: Configuración de entorno y dependencias.
- `STARTUP_GUIDE.md`: Guía rápida de inicio.

## 🔗 Componentes Relacionados
- **mcp-client**: Un cliente dedicado que se comunica con este servidor para ejecutar flujos de trabajo de automatización. Generalmente se encuentra en el directorio hermano del servidor.

---
*Este documento está diseñado para ser la primera lectura de un agente de IA que entra en el proyecto.*
