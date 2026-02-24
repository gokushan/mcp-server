# Use a slim Python image
FROM python:3.12-slim

# Install uv from image docker hub instead of download
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Create a non-root user and group
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser \
    && chown mcpuser:mcpuser /app

# Copy the project files
COPY --chown=mcpuser:mcpuser . .

# Install the project dependencies using uv
# --system flag to install in the system python since we are in a container
RUN uv pip install --system .

# Switch to the non-root user
USER mcpuser

# Expose the port the app runs on
EXPOSE 8081

# Command to run the application
CMD ["python", "-m", "glpi_mcp_server.server"]
