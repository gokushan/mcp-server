# Guía de Inicio del Servidor MCP GLPI

Esta guía explica las diferentes formas de arrancar y probar el servidor MCP.

## 1. Modos de Ejecución

Existen dos formas principales de ejecutar el servidor usando `fastmcp`:

### Modo Desarrollo (Con Inspector)
Este es el modo que estabas usando. Arranca el servidor y una interfaz web para pruebas.
```bash
uv run fastmcp dev src/glpi_mcp_server/server.py
```
*   **Ideal para:** Probar visualmente, ver logs en tiempo real y explorar la API.
*   **Interfaz:** Generalmente en `http://localhost:5173`.

### Modo SSE (Servidor de Red)
Arranca el servidor como un servicio web capaz de manejar múltiples conexiones simultáneas y persistentes.
```bash
uv run fastmcp run -t sse --port 8000 src/glpi_mcp_server/server.py
```
*   **Ideal para:** Simular despliegues remotos, conectar múltiples clientes o depurar notificaciones.
*   **Transporte:** Utiliza Server-Sent Events (SSE) para comunicación bidireccional.

---

## 2. Uso del MCP Inspector (Independiente)

Si tienes el servidor corriendo en modo SSE (o cualquier modo que no sea el `dev` integrado), puedes lanzar el Inspector de forma independiente para conectarte a él.

### Lanzar Inspector apuntando al servidor
Abre una terminal nueva y ejecuta:
```bash
npx -y @modelcontextprotocol/inspector http://localhost:8000/sse
```

### Configuración de Conexión en la Interfaz
Una vez abierto el Inspector en el navegador:
*   **Transport Type:** Selecciona `SSE`.
*   **URL:** `http://localhost:8000/sse`.
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

## 4. Uso con Clientes Reales (Recomendado)

La mejor forma de "ver" el servidor funcionando sin el inspector web es configurarlo en un cliente MCP como **Claude Desktop**.

1. Abre tu configuración de Claude Desktop.
2. Añade el servidor usando el **entry point** definido en el proyecto (esta es la forma recomendada):

```json
"glpi-server": {
  "command": "uv",
  "args": [
    "--directory", 
    "/home/gokushan/proyectos-mcp/glpi-mcp/server", 
    "run", 
    "glpi-mcp-server"
  ]
}
```

3. Reinicia Claude y verás las herramientas disponibles en el icono del martillo.

### Diferencia entre comandos
*   `uv run glpi-mcp-server`: Ejecuta tu aplicación oficial. Es lo que debes usar en "producción" o uso diario.
*   `fastmcp run ...`: Es una herramienta de utilidad. Úsala cuando quieras probar cambios rápidos o usar el Inspector (`fastmcp dev`).
