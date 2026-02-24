# Use a slim Python image
FROM python:3.12-slim

# Install uv from image docker hub instead of download
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Docker user configuration
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create a non-root user and group, handling potential existing IDs
RUN if getent group ${GROUP_ID} ; then \
    # If group exists, use it or rename it
    groupmod -n mcpuser $(getent group ${GROUP_ID} | cut -d: -f1); \
    else \
    groupadd -g ${GROUP_ID} mcpuser; \
    fi && \
    if getent passwd ${USER_ID} ; then \
    # If user exists, use it or rename it
    usermod -l mcpuser -g ${GROUP_ID} -d /app -m $(getent passwd ${USER_ID} | cut -d: -f1); \
    else \
    useradd -u ${USER_ID} -g ${GROUP_ID} -d /app -m mcpuser; \
    fi && \
    chown -R mcpuser:mcpuser /app

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
