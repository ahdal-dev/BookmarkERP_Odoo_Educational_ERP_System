# Educational ERP API Gateway - Project Structure

```
api_gateway/
│
├── nginx/                          # NGINX Reverse Proxy Configuration
│   ├── nginx.conf                  # Main NGINX configuration
│   └── ssl/                        # SSL certificates (generate locally)
│       ├── cert.pem
│       └── key.pem
│
├── fastapi_app/                    # FastAPI Gateway Application
│   ├── main.py                     # Main application file
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # FastAPI container build
│   └── __init__.py
│
├── prometheus/                     # Monitoring Configuration
│   ├── prometheus.yml              # Prometheus scrape config
│   └── data/                       # Metrics data (auto-generated)
│
├── grafana/                        # Visualization Configuration
│   ├── provisioning/               # Dashboard provisioning
│   └── data/                       # Grafana data (auto-generated)
│
├── logs/                           # Centralized logging
│   ├── nginx/
│   ├── fastapi/
│   ├── ocr/
│   └── odoo/
│
├── temp/                           # Temporary files
│   └── ocr_uploads/                # OCR file uploads
│
├── redis/                          # Redis cache data
│   └── data/
│
├── docker-compose.yml              # Container orchestration
├── .env.example                    # Environment variables template
├── .env                            # Actual environment config (git ignored)
├── .gitignore                      # Git ignore rules
├── README.md                       # Comprehensive documentation
├── setup.sh                        # Linux/Mac setup script
├── setup.ps1                       # Windows PowerShell setup script
└── test_api.ps1                    # API testing script

```

## Quick Reference

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f fastapi_gateway
```

### Rebuild After Changes
```bash
docker-compose up -d --build
```

### Scale FastAPI Gateway
```bash
docker-compose up -d --scale fastapi_gateway=3
```
