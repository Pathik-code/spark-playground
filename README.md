# ⚡ PySpark Playground

An interactive web-based PySpark cluster management and notebook environment.  
Configure your Spark cluster on the fly (with heterogeneous workers!) and write PySpark code in Jupyter notebooks with live cluster connectivity.

## ✨ Features

- 🎛️ **Dynamic Cluster Configuration**: 
  - configure **Per-Worker Resources** (e.g., Worker 1: 4GB/4Cores, Worker 2: 1GB/1Core)
  - Add/Remove workers dynamically
- 📓 **Integrated Jupyter Notebooks**: Create and manage notebooks with automatic Spark connection
- 📊 **Real-time Monitoring**: Live cluster status dashboard and logs
- 🐳 **Docker-based**: Fully containerized setup (Spark Master + Workers + Jupyter)
- 🚀 **Pre-built Templates**: DataFrames, SQL, ML, and more

---

## 🚀 Quick Start Guide

### Prerequisites
1. **Docker Desktop** installed and **running**
2. **Python 3.8+** (for the backend manager)
3. **Internal Ports Available**: 8000 (API), 8080 (Master UI), 8081+ (Worker UIs), 8888 (Jupyter)

### 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd pyspark-playground
   ```

2. **Set up Backend Environment**:
   It is recommended to use a virtual environment.
   ```bash
   cd backend
   python -m venv venv
   # Windows
   ..\venv\Scripts\activate
   # Mac/Linux
   source ../venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 🏃 Running the Application

1. **Start the Backend Manager**:
   Make sure you are in the `backend` directory with your environment activated.
   ```bash
   python main.py
   ```
   *You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`*

2. **Open the Web UI**:
   Open your browser to: **[http://localhost:8000](http://localhost:8000)**

3. **Start the Spark Cluster**:
   - Click the **"Start Cluster"** button in the UI.
   - Wait for the status to turn **Online**.

---

## 📖 Usage Guide

### 1. Configure Workers (Heterogeneous Cluster)
The Playground allows you to configure specific resources for *each* worker node.

1. Go to the **Worker Configuration** table in the UI.
2. **Add/Remove** workers using the buttons.
3. Set **Memory** (512MB - 8GB) and **Cores** (1 - 8) for each worker.
   - *Example: Create one "Heavy" worker (8GB) and two "Light" workers (1GB).*
4. Click **"✓ Apply Configuration & Restart"**.
   - *Note: This will restart the cluster to apply changes.*

### 2. Working with Notebooks
1. Click **"+ New Notebook"**.
2. Select a template (e.g., "DataFrame Basics", "SQL Queries").
3. Click **"Open"**.
4. Inside Jupyter, run the first cell to initialize the Spark Session.
   - *Note: Connectivity is pre-configured to `spark://spark-master:7077`.*

### 3. Monitoring
- **Spark Master UI**: [http://localhost:8080](http://localhost:8080)
- **Worker UIs**: Click the worker links in the Master UI (mapped to localhost:8081, 8082, etc.)
- **Logs**: View real-time cluster logs in the Playground UI bottom panel.

---

## 🔧 Troubleshooting

### "Failed to apply configuration"
- If you see an error about `WorkerConfig` validation, the backend might be running old code.
- **Fix**: Stop the backend (`Ctrl+C`) and start it again (`python main.py`).

### Cluster won't start / "Orphaned containers"
- The system attempts to clean up old containers automatically (`--remove-orphans`).
- If stuck, run manually in project root:
  ```bash
  docker-compose down --remove-orphans
  ```

### Cannot access Worker UI from Master
- Ensure you are using the links provided in the Master UI.
- We configure `SPARK_PUBLIC_DNS=localhost` so links work correctly on your host machine.

---

## 📁 Project Structure

```
pyspark-playground/
├── backend/                 # FastAPI Cluster Manager
│   ├── main.py             # Entry point
│   ├── cluster_manager.py  # Docker wrapper logic
│   └── ...
├── frontend/               # Local Web UI
│   ├── index.html
│   └── ...
├── docker/                 # Dockerfiles
├── notebooks/              # Saved User Notebooks
└── docker-compose.yml      # (Auto-generated) Do not edit manually
```

**Happy Sparking! ⚡**
