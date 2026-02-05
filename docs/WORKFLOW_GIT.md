# Flujo de Trabajo Git: Proyecto MCP Server

Este documento detalla el proceso para desarrollar en la rama `develop`, consolidar en `master` y publicar el proyecto en GitHub.

## 1. Configuración Inicial (Solo una vez)

Asegúrate de tener la rama `develop` creada localmente:

```bash
git checkout master
git checkout -b develop
```

## 2. Desarrollo Diario (Rama `develop`)

Para trabajar en nuevas funcionalidades o correcciones:

1.  **Cambiar a develop**:
    ```bash
    git checkout develop
    ```
2.  **Realizar cambios y confirmar**:
    ```bash
    git add .
    git commit -m "Descripción de los cambios"
    ```

## 3. Consolidación (Merge a `master`)

Cuando los cambios en `develop` estén listos y probados:

1.  **Cambiar a master**:
    ```bash
    git checkout master
    ```
2.  **Fusionar cambios**:
    ```bash
    git merge develop
    ```

## 4. Publicación en GitHub

Dado que este repositorio solo contiene el código del servidor, usaremos un proceso de publicación limpia para evitar subir historial con secretos antiguos.

### Pasos para publicar una nueva versión:

1.  **Crear Tag (Versionado)**:
    ```bash
    # Ejemplo para versión 0.2
    git tag 0.2
    ```

2.  **Generar Rama de Lanzamiento Limpia**:
    Ejecuta estos comandos en orden desde la raíz del proyecto para empaquetar solo el contenido de la carpeta `server`, limpiar el historial y subirlo.

    ```bash
    # 1. Definir la versión
    VERSION=0.2
    
    # 2. Extraer el contenido de la carpeta server a una rama temporal
    git subtree split --prefix server -b release/$VERSION
    
    # 3. Limpiar historial (Crear rama huérfana limpia)
    git checkout release/$VERSION
    git checkout --orphan release-clean-$VERSION
    git add -A
    git commit -m "Release $VERSION"
    
    # 4. Actualizar tag y subir
    # Mover el tag local a esta versión limpia
    git tag -f $VERSION
    
    # Subir a GitHub (Sustituye la rama main remota con esta versión limpia)
    git push origin release-clean-$VERSION:main --force
    git push origin $VERSION --force
    
    # 5. Limpieza local
    git checkout master
    git branch -D release/$VERSION
    git branch -D release-clean-$VERSION
    ```
