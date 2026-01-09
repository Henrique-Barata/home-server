# 🏠 Home Server Hub

Central management dashboard for home server applications. Start, stop, and monitor all your apps from one place.

## Features

- **Simple Dashboard**: Clean web interface to manage all apps
- **App Lifecycle Management**: Start, stop, and restart apps
- **Status Monitoring**: Real-time status of all applications
- **Container Ready**: Designed to work with Docker containers (future)

## Quick Start

### 1. Install Dependencies

```bash
cd hub
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Apps

Edit `config.yaml` to add your applications:

```yaml
apps:
  myapp:
    name: "My Application"
    description: "Description of my app"
    icon: "🚀"
    color: "#2196F3"
    path: "../myApp"
    entry: "run.py"
    port: 5001
```

### 3. Run the Hub

```bash
python run.py
```

The hub will be available at `http://localhost:8000`

## Configuration

### Hub Settings

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Host to bind to |
| `--port` | `8000` | Port to run on |
| `--debug` | `false` | Enable debug mode |

### App Configuration (config.yaml)

```yaml
apps:
  app_id:
    name: "Display Name"           # Required
    description: "App description" # Optional
    icon: "📦"                     # Emoji icon
    color: "#4CAF50"               # Accent color (hex)
    path: "../appFolder"           # Path to app directory
    entry: "run.py"                # Entry point script
    port: 5000                     # Port the app runs on
    host: "127.0.0.1"             # Host the app binds to
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard UI |
| `/api/apps` | GET | List all apps with status |
| `/api/apps/<id>/status` | GET | Get app status |
| `/api/apps/<id>/start` | POST | Start an app |
| `/api/apps/<id>/stop` | POST | Stop an app |
| `/api/apps/<id>/restart` | POST | Restart an app |
| `/api/apps/<id>/open` | GET | Get app URL |

## Architecture

```
home-server/
├── hub/                    # This hub application
│   ├── app/
│   │   ├── routes/        # API and UI routes
│   │   ├── services/      # App management logic
│   │   ├── templates/     # HTML templates
│   │   └── static/        # CSS, JS assets
│   ├── config.yaml        # App definitions
│   └── run.py             # Entry point
├── expensesApp/           # Your first app
└── futureApp/             # More apps...
```

## Future Plans

- [ ] Docker container support
- [ ] App health checks
- [ ] Resource monitoring (CPU, memory)
- [ ] Log viewing
- [ ] App auto-restart on failure
- [ ] Authentication

## License

MIT
