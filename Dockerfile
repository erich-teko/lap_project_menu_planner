FROM python:3.14

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/erich-teko/lap_project_menu_planner.git /app

# List files to verify
RUN ls -R

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Create volume mount point for database persistence
VOLUME ["/app/data"]

# Expose port
EXPOSE 80

# Run FastAPI application
CMD ["fastapi", "run", "main.py", "--port", "80", "--proxy-headers"]
