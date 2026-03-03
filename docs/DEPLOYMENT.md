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

## Requisitos Previos y Configuración de Servicios

Antes de desplegar el servidor, asegúrate de cumplir con los requisitos básicos y configurar correctamente los servicios externos.

### 1. Requisitos del Sistema
- **Python 3.10+**: Necesario solo para ejecutar  en modo desarrollo
 **Docker y Docker Compose**: Recomendado para simplificar el despliegue .
- **uv**: Gestión de paquetes Python ultrarrápida (usado internamente por el servidor).
- **Instancia de GLPI**: Versión 11.0.4.
- **Proveedor de LLM**: Cuenta local de Ollama con alguno de los siguientes modelos: Qwen, GLM, .... [Por deterrminar]. Es necesario tener instalado Ollama como motor de inferencia.Esta información tienes que configurarla en las variables de entorno del archivo `.env`. También se podría configurar para Claude y ChatGPT para usar modelos en la nube pero no se recomienda.

### 2. Configuración de GLPI (API REST)
El servidor MCP interactúa con GLPI exclusivamente a través de su API REST. Sigue estos pasos en la interfaz de GLPI:

1.  **Habilitar API REST**:
    -   Ve a `Configuración > General > API`.
    -   Activa `Habilitar la API Rest`.
    -   Activa `Habilitar el login con credenciales externas` (requerido para el uso de User Tokens).
    -   **Seguridad**: Si tienes activado el `Acceso restringido a la API`, debes añadir la dirección IP de donde corre este servidor MCP a la whitelist ("Whitelist de IPv4/IPv6") en esa misma pantalla.

2.  **Generar Token de Aplicación (App Token)**:
    -   En la misma pantalla de API, haz clic en "Añadir un nuevo token de aplicación".
    -   Dale un nombre descriptivo (ej: `MCP-Server-GLPI`).
    -   Copia el token generado. Este valor irá en la variable `GLPI_APP_TOKEN`.

3.  **Generar Token de Usuario (User Token)**:
    -   Entra en el perfil del usuario que realizará las acciones (clic en el nombre de usuario arriba a la derecha > `Perfil`).
    -   En la pestaña `Llave de acceso remoto`, haz clic en "Regenerar" (o copia el existente) bajo el campo "Token de la API".
    -   Este valor irá en la variable `GLPI_USER_TOKEN`.
    -   *Nota: Asegúrate de que este usuario tenga permisos suficientes dentro de GLPI para crear Documentos, Facturas y Contratos.*
4. **Permisos de usuario y acceso a contratos en GLPI**
    - Se recomienda crear un usuario específico con perfil super-admin en GLPI
    - Verificar que este usuario tiene permisos para gestionar contratos. Esto se verifica en al apartado `Administración > Perfiles > Gestión`

### 3. Configuración de Ollama (Local LLM)
Si optas por privacidad total o evitar costes de API, puedes usar Ollama:

1.  **Instalación**: Descarga e instala Ollama desde [ollama.com](https://ollama.com).
2.  **Preparar Modelo**: Descarga los lmodelos que vayas a usar Descárgalo ejecutando:
    ```bash
    ollama pull <modelo>
    ```
    *(Puedes usar otros modelos como `llama3` o `mistral` cambiando la variable `OLLAMA_MODEL`)*.
3.  **Configuración de Red (Linux/Docker)**:
    -   Para que el contenedor Docker pueda ver a Ollama en el host Linux, Ollama debe escuchar en todas las interfaces.
    -   Configura la variable de entorno `OLLAMA_HOST=0.0.0.0` en tu servicio de Ollama.
    -   En el archivo `.env` del MCP, usa la IP de la puerta de enlace de Docker (normalmente `http://172.17.0.1:11434`) como `OLLAMA_BASE_URL`.


---

## Despliegue con Docker (RECOMENDADO)

Este es el método más sencillo y robusto, ya que incluye todas las dependencias y garantiza que el entorno sea idéntico al de desarrollo.

### 1. Requisitos
- Docker y Docker Compose instalados.

### 2. Preparación
Copia los archivos esenciales (incluyendo `Dockerfile` y `docker-compose.yml`) al servidor remoto.

### 3. Configuración del entorno (`.env`)

Es fundamental configurar correctamente el archivo `.env`. A continuación se detallan las variables disponibles:

| Variable | Descripción | Ejemplo / Valor por defecto |
| :--- | :--- | :--- |
| **GLPI API** || |
| `GLPI_API_URL` | URL base de la API REST de GLPI. | `http://192.168.1.100:8080/apirest.php` |
| `GLPI_APP_TOKEN` | Token de aplicación generado en GLPI. | `your_app_token_here` |
| `GLPI_USER_TOKEN` | Token de usuario (API Token) de GLPI. | `your_user_token_here` |
| **OAuth 2.1** | (No usado, se ha añadido de forma opcional pero no esta operativo) | |
| `OAUTH_CLIENT_ID` | ID de cliente OAuth. | `client_id` |
| `OAUTH_CLIENT_SECRET` | Secreto de cliente OAuth. | `client_secret` |
| `OAUTH_AUTHORIZATION_URL` | URL de autorización OAuth. | `https://glpi.ex.com/oauth/authorize` |
| `OAUTH_TOKEN_URL` | URL de obtención de tokens OAuth. | `https://glpi.ex.com/oauth/token` |
| `OAUTH_REDIRECT_URI` | URI de redirección para el flujo OAuth. | `http://localhost:8080/callback` |
| **Versión (Tagging)** | | |
| `APP_VERSION` | Versión de la app (tag de la imagen Docker). | `v0.1.0` |
| **Transporte MCP** | | |
| `MCP_TRANSPORT` | Método de transporte del servidor. Usar siempre  `streamable-http` excepto para pruebas en local| `streamable-http` (o `stdio`, `sse`) |
| `MCP_HOST` | Host donde escuchará el servidor. | `0.0.0.0` (para aceptar conexiones externas) |
| `MCP_PORT` | Puerto donde escuchará el servidor. | `8081` |
| **LLM (Procesado)** | (Solo si usas herramientas de docs) | |
| `LLM_PROVIDER` | Proveedor de LLM a utilizar. | `openai`, `anthropic`, `ollama` |
| `OPENAI_API_KEY` | API Key de OpenAI. | `sk-...` |
| `ANTHROPIC_API_KEY` | API Key de Anthropic. | `sk-ant-...` |
| `OLLAMA_BASE_URL` | URL de tu instancia de Ollama. | `http://172.17.0.1:11434` |
| `OLLAMA_MODEL` | Modelo a utilizar en Ollama. | `llama2` |
| **Seguridad** | | |
| `GLPI_ALLOWED_ROOTS` | Rutas absolutas permitidas separadas por comas y sin espacios. | `/home/user/docs,/var/www/docs` |
| `GLPI_ALLOWED_EXTENSIONS`| Extensiones de archivo permitidas. | `pdf,txt,doc,docx` |
| `GLPI_FOLDER_SUCCESS` | Carpeta para archivos procesados con éxito. | `/home/user/procesados` |
| `GLPI_FOLDER_ERRORES` | Carpeta para archivos que fallaron. | `/home/user/errores` |
| **Traducción de Rutas** | (Solo para Docker) | |
| `GLPI_HOST_ALLOWED_ROOTS`| Rutas reales en el ho. | `/home/gokushan/docs,...` |
| `GLPI_HOST_FOLDER_SUCCESS`| Ruta real del host para archivos procesados. | `/home/gokushan/exito` |
| `GLPI_HOST_FOLDER_ERRORES`| Ruta real del host para archivos con errores. | `/home/gokushan/error` |
| **Configuración LLM Avanzada** | | |
| `LLM_MAX_CHARS` | Máximo de caracteres a procesar por doc. | `50000` |
| `TIMEOUT_LLM` | Timeout para respuestas del LLM (seg). | `600.0` |
| `LLM_MOCK` | Activa el modo de simulación (Mock) para evitar llamar al LLM en pruebas. | `true` / `false` |
| **Logging** | | |
| `LOG_LEVEL` | Nivel de detalle de los logs. | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| **Docker (Avanzado)** | (Configuración de volúmenes y permisos) | |
| `USER_ID` | UID del usuario host (para permisos). | `1000` |
| `GROUP_ID` | GID del usuario host (para permisos). | `1000` |
| `DOCKER_HOST_PATH_*` | Rutas en tu equipo host. | Ver sección de volúmenes abajo. |

> [!IMPORTANT]
> Si despliegas con Docker, recuerda que `localhost` se refiere al contenedor. Para conectar con GLPI usa la IP del host o el nombre del servicio en la red de Docker.

---

## Configuración Avanzada de Docker (Volúmenes y Permisos)

Para garantizar la portabilidad y evitar problemas de permisos al mover archivos entre el host y el contenedor, se ha implementado un sistema dinámico.

### 1. Mapeo de Volúmenes Dinámicos
En el archivo `.env`, debes definir las rutas de tu equipo host que quieres que el contenedor pueda ver. Estas variables se usan en el `docker-compose.yml`:

- `DOCKER_HOST_PATH_FACTURAS`: Ruta a tus facturas.
- `DOCKER_HOST_PATH_CONTRATOS1`: Ruta a contratos (tipo 1).
- `DOCKER_HOST_PATH_CONTRATOS2`: Ruta a contratos (tipo 2).
- `DOCKER_HOST_PATH_BATCH`: Ruta para procesamiento por lotes.
- `DOCKER_HOST_PATH_PROCESADOS`: Donde se moverán los archivos con éxito.
- `DOCKER_HOST_PATH_ERRORES`: Donde se moverán los archivos fallidos.

Internamente, el contenedor mapea estas rutas a subcarpetas de `/app/data/` (ej: `/app/data/facturas`), lo que permite que la aplicación funcione de forma idéntica independientemente de dónde estén tus archivos en el host.

### 2. Gestión de Permisos (UID/GID)
Linux gestiona los permisos mediante números de ID de usuario. Para que el proceso dentro del contenedor pueda mover archivos pertenecientes a tu usuario del host:

1. El contenedor crea un usuario llamado `mcpuser`.
2. Durante la construcción (`docker compose build`), se le asignan los IDs definidos en `USER_ID` y `GROUP_ID`.
3. Por defecto son `1000`, que es el ID estándar del primer usuario en sistemas Linux como Ubuntu.
4. Si tu ID es distinto, cámbialo en el `.env` antes de compilar.

> [!TIP]
> Puedes saber tu ID actual ejecutando `id -u` e `id -g` en tu terminal.


### 4. Ejecución
```bash
docker compose up -d --build
```
El servidor estará disponible en el puerto **8081** (ruta `/mcp`).

---

## Capa de Traducción de Rutas (Host vs Contenedor)

Cuando el servidor corre en Docker, las rutas internas (`/app/data/...`) son diferentes de las rutas fuera de Docker (`/home/user/...`). Para que el cliente MCP vea siempre tus rutas reales, se usa una **Capa de Traducción**:

- **¿Cómo funciona?**: El servidor lee archivos en la ruta del contenedor pero le dice al cliente MCP que están en la ruta del host.
- **Configuración**: 
    1. Define tus rutas reales en las variables `GLPI_HOST_*`.
    2. Asegúrate de que el orden de las rutas en `GLPI_HOST_ALLOWED_ROOTS` coincida con el de `GLPI_ALLOWED_ROOTS`.
- **Beneficio**: No necesitas cambiar nada en tu cliente MCP si alternas entre ejecutar el servidor en local o en Docker; las rutas reportadas serán siempre las mismas.

---


### 5. Conexión desde el Cliente (Claude Desktop)

Una vez el servidor está corriendo en tu servidor remoto (ej. `mcp.tu-dominio.com`), puedes conectar Claude Desktop usando un puente y usarlo como mcp server:

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
