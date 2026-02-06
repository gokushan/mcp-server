# Guía de Despliegue Remoto: GLPI MCP Server

Para traspasar y ejecutar este proyecto en otro equipo, solo necesitas los archivos esenciales del servidor. **No es necesario (ni recomendable) copiar los entornos virtuales o carpetas de herramientas internas.**

## Archivos Necesarios para el Despliegue

Copia únicamente los siguientes archivos y carpetas de la subcarpeta `server/` al servidor remoto:

1.  **`src/`**: Contiene todo el código fuente del servidor.
2.  **`pyproject.toml`**: Define las dependencias y la configuración del proyecto.
3.  **`uv.lock`**: Asegura que se instalen exactamente las mismas versiones de las librerías.
4.  **`.env.example`**: Plantilla para la configuración (el archivo `.env` real **NO** se debe compartir si contiene claves reales, se debe crear uno nuevo en el destino).
5.  **`README.md`**: Referencia principal en la raíz.
6.  **`docs/`**: Carpeta con guías detalladas (`STARTUP_GUIDE.md`, `DEPLOYMENT.md`, `architecture.md`, etc.).

### Archivos que NO debes copiar
- `.venv/`: El entorno se debe regenerar en el destino para evitar incompatibilidades de sistema.
- `.git/`: No es necesario para la ejecución (a menos que quieras seguir usando Git allí).
- `__pycache__/`: Archivos temporales de Python.
- `.vscode/`: Configuraciones locales de tu editor.

---

## Opción A: Despliegue con Docker (RECOMENDADO)

Este es el método más sencillo y robusto, ya que incluye todas las dependencias y garantiza que el entorno sea idéntico al de desarrollo.

### 1. Requisitos
- Docker y Docker Compose instalados.

### 2. Preparación
Copia los archivos esenciales (incluyendo `Dockerfile` y `docker-compose.yml`) al servidor remoto.

### 3. Configuración del entorno (`.env`)
Es fundamental que las URLs de GLPI usen la IP del host o un dominio real, ya que `localhost` dentro de Docker no alcanzará a tu máquina.
```bash
# Ejemplo en .env
GLPI_API_URL=http://192.168.71.129:8080/apirest.php
OAUTH_REDIRECT_URI=http://192.168.71.129:8080/callback
```

### 4. Ejecución
```bash
docker compose up -d --build
```
El servidor estará disponible en el puerto **8081** (ruta `/mcp`).

---

## Opción B: Despliegue Manual (Systemd)

Crea un archivo de servicio para que el servidor se inicie automáticamente y se reinicie en caso de fallo:

`sudo nano /etc/systemd/system/glpi-mcp.service`

```ini
[Unit]
Description=GLPI MCP Server (HTTP)
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/home/tu_usuario/proyectos-mcp/glpi-mcp/server
# Carga las variables de entorno desde el archivo .env
EnvironmentFile=/home/tu_usuario/proyectos-mcp/glpi-mcp/server/.env
ExecStart=/home/tu_usuario/.local/bin/uv run fastmcp run src/glpi_mcp_server/server.py --transport http --port 8000
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
        
        # Importante para Streamable HTTP
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### 3. Conexión desde el Cliente (Claude Desktop)

Una vez el servidor está corriendo en tu servidor remoto (ej. `mcp.tu-dominio.com`), puedes conectar Claude Desktop usando un puente:

```json
{
  "mcpServers": {
    "glpi-docker": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8081/mcp"
      ]
    }
  }
}
```
*(Nota: Cambia `localhost` por la IP o dominio de tu servidor si es remoto).*

---

## Requisitos del Servidor Remoto
- **Python 3.10+** instalado.
- **uv** instalado globalmente o en el path del usuario.
- Conectividad HTTPS (puerto 443) abierta hacia el exterior si usas Nginx.
- Conectividad con la instancia de GLPI.
