import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DOCKER_DIR = BASE_DIR / "docker"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
TEMPLATES_DIR = NOTEBOOKS_DIR / "templates"
USER_NOTEBOOKS_DIR = NOTEBOOKS_DIR / "user"
DATA_DIR = BASE_DIR / "data"

# Docker configuration
DOCKER_COMPOSE_TEMPLATE = DOCKER_DIR / "docker-compose.template.yml"
DOCKER_COMPOSE_FILE = BASE_DIR / "docker-compose.yml"

# Backend configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

# Cluster configuration
DEFAULT_WORKER_COUNT = int(os.getenv("DEFAULT_WORKER_COUNT", "2"))
DEFAULT_WORKER_MEMORY = os.getenv("DEFAULT_WORKER_MEMORY", "1g")
DEFAULT_WORKER_CORES = int(os.getenv("DEFAULT_WORKER_CORES", "1"))

# Jupyter configuration
JUPYTER_PORT = int(os.getenv("JUPYTER_PORT", "8888"))
JUPYTER_URL = f"http://localhost:{JUPYTER_PORT}"

# Spark configuration
SPARK_MASTER_PORT = int(os.getenv("SPARK_MASTER_PORT", "7077"))
SPARK_MASTER_WEBUI_PORT = int(os.getenv("SPARK_MASTER_WEBUI_PORT", "8080"))
SPARK_MASTER_URL = f"spark://localhost:{SPARK_MASTER_PORT}"
SPARK_MASTER_UI_URL = f"http://localhost:{SPARK_MASTER_WEBUI_PORT}"

# Ensure directories exist
NOTEBOOKS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
USER_NOTEBOOKS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
