# Guía de Inicio del Servidor MCP GLPI

Esta guía explica las diferentes formas de arrancar y probar el servidor MCP.

> [!NOTE]
> Todos los comandos de esta guía deben ejecutarse desde la carpeta raíz del servidor (`server/`).

## 1. Modos de Ejecución

Existen dos formas principales de ejecutar el servidor usando `fastmcp`:

### Modo Desarrollo (Con Inspector)
Este es el modo que estabas usando. Arranca el servidor en modo STDIO/STDOUT y una interfaz web para pruebas.
```bash
uv run fastmcp dev src/glpi_mcp_server/server.py
```
*   **Ideal para:** Probar visualmente, ver logs en tiempo real y explorar la API.
*   **Interfaz:** Generalmente en `http://localhost:5173`.

### Modo SSE (Server-Sent Events)
Arranca el servidor usando el transporte SSE. Útil para compatibilidad con clientes más antiguos.
```bash
uv run fastmcp run -t sse --port 8000 src/glpi_mcp_server/server.py
```
*   **Transporte:** Utiliza Server-Sent Events (SSE). La URL por defecto es `http://localhost:8000/sse`.

### Modo HTTP (Streamable HTTP) - RECOMENDADO LOCAL
Es el modo más moderno y eficiente para ejecución local fuera de Docker.
```bash
uv run fastmcp run -t http --port 8000 src/glpi_mcp_server/server.py
```
*   **Ideal para:** Máximo rendimiento en local y cumplimiento con los últimos estándares de MCP.
*   **Transporte:** Utiliza Streamable HTTP. La URL por defecto es `http://localhost:8000/mcp`.

### Modo Docker (Contenedor) - IDEAL PARA DESPLIEGUE
Arranca el servidor de forma aislada. Este modo usa el puerto **8081** por defecto para no interferir con otros servicios.
```bash
docker compose up -d
```
*   **Ideal para:** Entornos de producción o pruebas rápidas sin configurar Python localmente.
*   **Transporte:** Streamable HTTP. La URL es `http://localhost:8081/mcp`.
*   **Requisito:** El archivo `.env` debe usar la IP de tu máquina (ej. `192.168.71.129`) en lugar de `localhost` para conectar con GLPI.

---

## 2. Uso del MCP Inspector (Independiente)

Si tienes el servidor corriendo en modo HTTP o Docker, puedes lanzar el Inspector de forma independiente para conectarte a él.

### Lanzar Inspector apuntando al servidor

**Si ejecutas localmente (puerto 8000):**
```bash
npx -y @modelcontextprotocol/inspector@latest http://localhost:8000/mcp
```

**Si ejecutas con Docker (puerto 8081):**
```bash
npx -y @modelcontextprotocol/inspector@latest http://localhost:8081/mcp
```

Si usas **SSE**:
```bash
npx -y @modelcontextprotocol/inspector@latest http://localhost:8000/sse
```

### Configuración de Conexión en la Interfaz
Una vez abierto el Inspector en el navegador:
*   **Transport Type:** Selecciona `HTTP` o `SSE` según corresponda.
*   **URL:** `http://localhost:8000/mcp` (para HTTP) o `http://localhost:8000/sse` (para SSE).
*   **Connection Type:** Se recomienda **Via Proxy** para evitar problemas de CORS en desarrollo local.

### Modo Normal (Standard I/O)
Este modo arranca el servidor en "silencio", esperando comandos JSON-RPC por `stdin`. Es como lo usaría Claude Desktop.
```bash
uv run fastmcp run src/glpi_mcp_server/server.py
```
*   **Ideal para:** Integración con clientes (Claude, IDEs) o pruebas manuales por terminal.
*   **Nota:** No verás logs ni mensajes de bienvenida, el servidor queda esperando entrada.

---

## 3. Pruebas Manuales por Terminal

Si quieres enviar comandos manualmente en el **Modo Normal**, debes enviar objetos JSON válidos según el protocolo MCP.

> [!IMPORTANT]
> **El primer comando debe ser `initialize`**. El servidor MCP rechazará cualquier petición de herramientas o recursos si no se ha inicializado la sesión primero.

### Paso 1: Inicializar la sesión
Copia y pega este comando al arrancar el servidor:

```json
{ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": { "protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": { "name": "terminal-test", "version": "1.0" } } }
```

### Paso 2: Listar Herramientas o Recursos
Una vez inicializado, ya puedes enviar otros comandos:

**Listar Herramientas:**
```json
{ "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {} }
```

**Listar Recursos:**
```json
{ "jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {} }
```

---

### Configuración para el Contenedor (Docker)
Si prefieres usar la versión Docker, añade esta configuración:

```json
"glpi-docker": {
  "command": "npx",
  "args": [
    "-y",
    "mcp-remote",
    "http://localhost:8081/mcp"
  ]
}
```

---

## 5. Notas sobre Puertos y Prioridad

### ¿Qué puerto se usa?
*   **Si ejecutas con `docker compose`**: El puerto está fijado en el `8081` (configurable en `server.py` vía `MCP_PORT`).
*   **Si usas la CLI `fastmcp`**: El flag `--port` que pases por terminal tiene **prioridad total**. 
    *   Ejemplo: `uv run fastmcp run --port 8000 ...` ignorará el puerto `8081` definido en el código.

Esto es así porque cuando usas la herramienta `fastmcp`, esta importa tu servidor pero aplica su propia configuración de arranque, saltándose el bloque `if __name__ == "__main__":` de tu archivo `server.py`.
