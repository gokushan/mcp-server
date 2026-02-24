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

Es fundamental configurar correctamente el archivo `.env`. A continuación se detallan las variables disponibles:

| Variable | Descripción | Ejemplo / Valor por defecto |
| :--- | :--- | :--- |
| **GLPI API** | | |
| `GLPI_API_URL` | URL base de la API REST de GLPI. | `http://192.168.1.100:8080/apirest.php` |
| `GLPI_APP_TOKEN` | Token de aplicación generado en GLPI. | `your_app_token_here` |
| `GLPI_USER_TOKEN` | Token de usuario (API Token) de GLPI. | `your_user_token_here` |
| **OAuth 2.1** | (Opcional si se usa User Token) | |
| `OAUTH_CLIENT_ID` | ID de cliente OAuth. | `client_id` |
| `OAUTH_CLIENT_SECRET` | Secreto de cliente OAuth. | `client_secret` |
| `OAUTH_AUTHORIZATION_URL` | URL de autorización OAuth. | `https://glpi.ex.com/oauth/authorize` |
| `OAUTH_TOKEN_URL` | URL de obtención de tokens OAuth. | `https://glpi.ex.com/oauth/token` |
| `OAUTH_REDIRECT_URI` | URI de redirección para el flujo OAuth. | `http://localhost:8080/callback` |
| **Transporte MCP** | | |
| `MCP_TRANSPORT` | Método de transporte del servidor. | `streamable-http` (o `stdio`, `sse`) |
| `MCP_HOST` | Host donde escuchará el servidor. | `0.0.0.0` (para aceptar conexiones externas) |
| `MCP_PORT` | Puerto donde escuchará el servidor. | `8081` |
| **LLM (Procesado)** | (Solo si usas herramientas de docs) | |
| `LLM_PROVIDER` | Proveedor de LLM a utilizar. | `openai`, `anthropic`, `ollama` |
| `OPENAI_API_KEY` | API Key de OpenAI. | `sk-...` |
| `ANTHROPIC_API_KEY` | API Key de Anthropic. | `sk-ant-...` |
| **Seguridad** | | |
| `GLPI_ALLOWED_ROOTS` | Rutas absolutas permitidas (CSV). | `/home/user/docs,/var/www/docs` |
| `GLPI_ALLOWED_EXTENSIONS`| Extensiones de archivo permitidas. | `pdf,txt,doc,docx` |

> [!IMPORTANT]
> Si despliegas con Docker, recuerda que `localhost` se refiere al contenedor. Para conectar con GLPI usa la IP del host o el nombre del servicio en la red de Docker.


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

---

## Usuarios y Permisos Recomendados

Para un despliegue seguro en entornos Linux (tanto con Docker como manual), sigue estas recomendaciones:

### 1. Usuario de Ejecución
- **NUNCA ejecutes la aplicación como `root`**.
- En Docker, la imagen ya está configurada para usar el usuario `mcpuser`.
- En instalaciones manuales, crea un usuario dedicado sin privilegios de sudo:
  ```bash
  sudo useradd -m -s /bin/bash mcp_service
  ```

### 2. Permisos de Archivos y Carpetas
La aplicación necesita diferentes niveles de acceso según la funcionalidad:

| Ruta | Permiso Requerido | Razón |
| :--- | :--- | :--- |
| **Código fuente (`src/`)** | Lectura (`r`) | Ejecución del código Python. |
| **Raíces permitidas (`GLPI_ALLOWED_ROOTS`)** | Lectura (`r`) | Para que el proceso pueda leer los documentos a procesar. |
| **Carpeta de Éxito (`GLPI_FOLDER_SUCCESS`)** | Lectura y Escritura (`rw`) | Para mover los archivos procesados correctamente. |
| **Carpeta de Errores (`GLPI_FOLDER_ERRORES`)** | Lectura y Escritura (`rw`) | Para mover los archivos que fallaron. |

**Ejemplo de configuración de permisos:**
Si tu usuario es `mcpuser` y tus documentos están en `/opt/mcp/docs`:
```bash
# Cambiar el propietario de la carpeta de documentos
sudo chown -R mcpuser:mcpuser /opt/mcp/docs

# Asegurar permisos de lectura/escritura para el propietario
chmod -R 755 /opt/mcp/docs
```

### 3. Consideraciones de Seguridad
- **Variables de Entorno**: Asegúrate de que el archivo `.env` solo sea legible por el usuario que ejecuta el servicio (`chmod 600 .env`).
- **Acceso a Red**: Si usas un Proxy Inverso (Nginx), el cortafuegos solo debería permitir tráfico entrante al puerto del proxy (80/443), manteniendo el puerto de la aplicación (8000/8081) cerrado al exterior.
