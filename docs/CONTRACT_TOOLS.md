# Herramientas de Gestión de Contratos

Este documento detalla las herramientas (tools) disponibles en el servidor MCP para la gestión de contratos en GLPI. Todas estas funciones están expuestas a través del protocolo MCP y pueden ser invocadas por modelos de IA.

## Listado de Herramientas

### 1. `create_glpi_contract`
Crea un nuevo contrato en GLPI. Permite adjuntar un documento (PDF, etc.) de forma opcional durante la creación.

*   **Parámetros principales**:
    *   `name` (Obligatorio): Nombre del contrato.
    *   `num`: Número de contrato.
    *   `begin_date`: Fecha de inicio (YYYY-MM-DD).
    *   `duration`: Duración en meses.
    *   `cost`: Coste del contrato.
    *   `file_path`: Ruta absoluta al documento del contrato para adjuntarlo automáticamente.
*   **Comportamiento**: Valida los datos contra el modelo `ContractData`, realiza el POST a GLPI y, si se incluye `file_path`, sube el archivo a la sección de documentos y lo vincula.

### 2. `get_contract_status_by_id`
Recupera todos los detalles y el estado actual de un contrato específico.

*   **Parámetros**:
    *   `id` (Obligatorio): ID del contrato.

### 3. `search_contracts`
Busca contratos basados en criterios flexibles.

*   **Parámetros**:
    *   `name`: Parte del nombre del contrato.
    *   `num`: Parte del número de contrato.
    *   `id`: ID específico.
    *   `limit`: Máximo de resultados (por defecto 20).

### 4. `attach_document_to_contract`
Adjunta un documento a un contrato que ya existe. Útil si la creación falló o si se quieren añadir documentos adicionales posteriormente.

*   **Parámetros**:
    *   `contract_id` (Obligatorio): ID del contrato.
    *   `file_path` (Obligatorio): Ruta absoluta al archivo.
    *   `document_name`: Nombre sugerido para el documento en GLPI.

### 5. `delete_glpi_contract`
Elimina un contrato y, opcionalmente, todos sus documentos asociados para mantener la limpieza del sistema.

*   **Parámetros**:
    *   `contract_id` (Obligatorio): ID del contrato a eliminar.
    *   `force_purge`: Si es `True`, elimina permanentemente (purgar). Si es `False`, lo mueve a la papelera (comportamiento por defecto).

## Notas Técnicas
*   **Validación de Rutas**: Todas las herramientas que aceptan `file_path` verifican que la ruta esté dentro de los directorios permitidos configurados en el entorno (`ALLOWED_ROOTS`).
*   **Extensiones**: Solo se permiten las extensiones de archivo configuradas en las variables de entorno para la subida de documentos.
