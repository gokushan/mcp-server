# Guía de Despliegue Remoto: GLPI MCP Server

Para traspasar y ejecutar este proyecto en otro equipo, solo necesitas los archivos esenciales del servidor. **No es necesario (ni recomendable) copiar los entornos virtuales o carpetas de herramientas internas.**

## Archivos Necesarios para el Despliegue

Copia únicamente los siguientes archivos y carpetas de la subcarpeta `server/` al servidor remoto:

1.  **`src/`**: Contiene todo el código fuente del servidor.
2.  **`pyproject.toml`**: Define las dependencias y la configuración del proyecto.
3.  **`uv.lock`**: Asegura que se instalen exactamente las mismas versiones de las librerías.
4.  **`.env.example`**: Plantilla para la configuración (el archivo `.env` real **NO** se debe compartir si contiene claves reales, se debe crear uno nuevo en el destino).
5.  **`README.md`** y **`STARTUP_GUIDE.md`**: Para referencia de uso.

### Archivos que NO debes copiar
- `.venv/`: El entorno se debe regenerar en el destino para evitar incompatibilidades de sistema.
- `.git/`: No es necesario para la ejecución (a menos que quieras seguir usando Git allí).
- `__pycache__/`: Archivos temporales de Python.
- `.vscode/`: Configuraciones locales de tu editor.

---

## Pasos para la Instalación en el Remoto

Una vez copiados los archivos al nuevo equipo, sigue estos pasos:

1.  **Instalar `uv`** (recomendado):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Crear el archivo de configuración**:
    ```bash
    cp .env.example .env
    # Edita el archivo .env con las credenciales del nuevo entorno
    nano .env
    ```

3.  **Instalar dependencias y preparar el entorno**:
    ```bash
    uv sync
    ```

4.  **Ejecutar el servidor**:
    - **Para probar**: `uv run fastmcp dev src/glpi_mcp_server/server.py`
    - **Para producción**: `uv run fastmcp run src/glpi_mcp_server/server.py`

## Gestión en Producción

Para un entorno de producción estable y accesible remotamente, se recomienda usar el transporte **SSE (Server-Sent Events)** y un gestor de procesos como **systemd**.

### 1. Configuración de systemd (Daemonización)

Crea un archivo de servicio para que el servidor se inicie automáticamente y se reinicie en caso de fallo:

`sudo nano /etc/systemd/system/glpi-mcp.service`

```ini
[Unit]
Description=GLPI MCP Server (SSE)
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/home/tu_usuario/proyectos-mcp/glpi-mcp/server
# Carga las variables de entorno desde el archivo .env
EnvironmentFile=/home/tu_usuario/proyectos-mcp/glpi-mcp/server/.env
ExecStart=/home/tu_usuario/.local/bin/uv run fastmcp run src/glpi_mcp_server/server.py --transport sse --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Comandos útiles:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable glpi-mcp
sudo systemctl start glpi-mcp
sudo systemctl status glpi-mcp
```

### 2. Acceso Remoto Seguro (Nginx / HTTPS)

No se recomienda exponer el puerto 8000 directamente a internet. Usa un proxy inverso como Nginx con SSL (Certbot):

```nginx
server {
    server_name mcp.tu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Importante para SSE
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### 3. Conexión desde el Cliente (Claude Desktop)

Una vez el servidor está corriendo en `https://mcp.tu-dominio.com/sse`, configúralo en tu local:

```json
{
  "mcpServers": {
    "glpi-prod": {
      "url": "https://mcp.tu-dominio.com/sse"
    }
  }
}
```

---

## Requisitos del Servidor Remoto
- **Python 3.10+** instalado.
- **uv** instalado globalmente o en el path del usuario.
- Conectividad HTTPS (puerto 443) abierta hacia el exterior si usas Nginx.
- Conectividad con la instancia de GLPI.
