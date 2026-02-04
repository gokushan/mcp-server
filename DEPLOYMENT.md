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

---

## Requisitos del Servidor Remoto
- **Python 3.10+** instalado.
- Acceso a internet para descargar dependencias la primera vez.
- Conectividad con la instancia de GLPI.
