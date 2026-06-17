# Setup Guide: Multi-Organization RAG Chatbot Platform

This guide provides step-by-step instructions to configure, initialize, and run the Multi-Organization RAG Chatbot Platform.

---

## Prerequisites

Before starting, ensure you have the following installed and configured on your system:

1. **Python 3.10+**: Ensure Python is added to your system's PATH.
2. **PostgreSQL**: A running instance of PostgreSQL.
3. **pgvector Extension**: The PostgreSQL extension for vector search.
   - For Windows, you can install it using pre-built binaries or build it from source.
   - For Docker, you can use the official `pgvector/pgvector:pg16` image.
4. **Google Gemini API Key**: Needed for language generation, query rewriting, and evaluation. Get a key from [Google AI Studio](https://aistudio.google.com/).

---

## Step 1: Set Up PostgreSQL & Enable pgvector

1. Connect to your PostgreSQL server and create a database for the project (e.g., `mydb`):
   ```sql
   CREATE DATABASE mydb;
   ```
2. Connect to the newly created database and enable the `pgvector` extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
   > [!IMPORTANT]
   > The `pgvector` extension is required before running the database setup scripts. If this extension is missing, the schema creation will fail because the `Vector` type will not be recognized.

---

## Step 2: Configure Environment Variables

1. Copy the template environment file to create your local configuration:
   - **Using Terminal/Bash**:
     ```bash
     cp .env.example .env
     ```
   - **Using PowerShell**:
     ```powershell
     Copy-Item .env.example .env
     ```
2. Open the newly created `.env` file and configure the values:
   - **`DATABASE_URL`**: Update this URL with your PostgreSQL user, password, host, port, and database name.
     - *Format*: `postgresql+psycopg2://<username>:<password>@<host>:<port>/<dbname>`
     - *Example*: `postgresql+psycopg2://postgres:mysecretpassword@localhost:5432/mydb`
   - **`GEMINI_API_KEY`**: Set your actual Google Gemini API key.
   - **`SMTP_*`** (Optional): If you want to enable automatic email notifications when creating new admins/users. If left unconfigured, credentials will be printed to the backend console (mocked).

---

## Step 3: Install Dependencies

You can set up the virtual environment and install packages either automatically using `make` or manually.

### Option A: Using the Makefile (Recommended)
At the root directory of the project, run:
```bash
make install
```
This target will:
- Create a Python virtual environment (`venv`).
- Upgrade pip.
- Install all dependencies listed in `Backend/requirements.txt`.

### Option B: Manual Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```
2. **Activate the virtual environment**:
   - **Windows (Command Prompt)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Unix/macOS (Bash/Zsh)**:
     ```bash
     source venv/bin/activate
     ```
3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r Backend/requirements.txt
   ```

---

## Step 4: Initialize Database & Create Super-Admin

Running the super-admin setup script will automatically generate all necessary database tables and create the root super-admin account.

### Option A: Using the Makefile
At the root directory, run (replace `admin` and `password123` with your desired credentials):
```bash
make superadmin USERNAME=admin PASSWORD=password123
```

### Option B: Manual Execution
With the virtual environment activated, navigate to the `Backend` directory and execute:
```bash
cd Backend
python setup_super_admin.py admin password123
```

---

## Step 5: Verify Setup (Optional)

Run the test suite to ensure database connectivity and model registrations are functioning correctly:

### Option A: Using the Makefile
```bash
make test
```

### Option B: Manual Execution
```bash
cd Backend
python test.py
python test_models.py
```

---

## Step 6: Run the Server

Start the FastAPI application.

### Option A: Using the Makefile
At the root directory, run:
```bash
make run
```

### Option B: Manual Execution
With the virtual environment activated, navigate to the `Backend` directory and start Uvicorn:
```bash
cd Backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Step 7: Access the Platform

Once the server is running, you can access the frontend dashboard and APIs:

- **Welcome Page**: [http://localhost:8000/](http://localhost:8000/)
- **Login / Dashboards**: Go to the login page at [http://localhost:8000/login](http://localhost:8000/login)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

### First-Time Platform Workflow

1. Go to [http://localhost:8000/login](http://localhost:8000/login).
2. Log in using your **Super-Admin** credentials (created in Step 4).
3. In the Super-Admin panel:
   - Create one or more **Organizations** (e.g., "Insurance Department").
   - Create an **Admin** user for each organization.
4. Log out of Super-Admin, and log in as the newly created **Organization Admin**.
   - Since a temporary password was generated, click the link in the console output (or check your email if SMTP is configured) to reset the password.
5. In the Admin Dashboard:
   - Create regular **Users** under your organization.
   - Go to the **Documents** tab and upload reference files (PDF, DOCX, TXT, CSV). They will be processed, chunked, and embedded into your vector database automatically.
6. Log out, and log in as a **Regular User** to begin chatting! The chatbot will answer strictly using the context from your organization's uploaded documents.
