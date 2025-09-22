# Command Snippet Manager

A desktop application for managing and executing shell command snippets that you use frequently.

## 📋 Description

**Command Snippet Manager** is a GUI application developed in Python with PyQt6 that allows you to store, organize, and quickly execute complex shell commands that you use frequently. Perfect for platform engineers, DevOps, and developers who work with tools like `aws-vault`, `kubectl`, `ssh`, `docker`, and more.

### ✨ Key Features

- 📝 **Complete Snippet Management**: Create, edit, delete, and view command snippets
- 🔍 **Advanced Search**: Real-time filtering by name, description, command, or tags
- 📋 **Quick Copy**: Copy commands to clipboard with a single click
- 🚀 **Direct Execution**: Execute commands directly in Terminal.app (macOS)
- 🏷️ **Tag System**: Organize snippets with comma-separated tags
- 📊 **Usage Tracking**: Automatically tracks when each snippet was last used
- 💾 **Local Database**: SQLite storage with no external dependencies
- 🎨 **Modern Interface**: Native macOS design with keyboard shortcuts

## 🚀 Installation and Setup

### Prerequisites

- **Python 3.9+** installed on your system
- **macOS** (the application is optimized for macOS, though it may work on other systems)

### Automatic Installation

1. **Clone or download the project**:
   ```bash
   git clone <your-repo-url>
   cd my_snippet_app
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This script:
   - Creates a Python virtual environment
   - Installs necessary dependencies
   - Sets up the project to run

### Manual Installation

If you prefer to install manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Using the Application

### Running the Application

**Option 1: Run script (recommended)**
```bash
./run.sh
```

**Option 2: Manual execution**
```bash
source venv/bin/activate
python main.py
```

### Main Interface

The application opens with a main window containing:

- **Snippets Table**: Shows all your saved commands
- **Search Bar**: Filters snippets in real-time
- **Preview Panel**: Shows the command of the selected snippet
- **Action Buttons**: New, Edit, Delete, Copy, Execute

### Creating a New Snippet

1. Click **"New Snippet"** or press `Ctrl+N`
2. Fill in the fields:
   - **Name** *(required)*: A short, descriptive name
     - You can have multiple snippets with the same name
     - Each snippet maintains its own unique ID
   - **Description**: Detailed explanation of the command's purpose
   - **Command** *(required)*: The command to execute (can be multi-line)
   - **Tags**: Comma-separated tags for organization
3. Click **"Save"** or press `Ctrl+Enter`

> **Note**: The application allows multiple snippets with the same name, which is useful for storing variations of similar commands (e.g., different environments or parameters).

### Managing Existing Snippets

- **Edit**: Select a snippet and click "Edit" or double-click the row
- **Delete**: Select a snippet and click "Delete" (confirmation will be requested)
- **Search**: Type in the search bar to filter by any field
- **Sort**: Click column headers to sort

### Using Snippets

- **Copy to Clipboard**: Select a snippet and click "Copy Command" or press `Ctrl+C`
- **Execute Command**: Select a snippet and click "Execute" or press `Ctrl+E`
  - A new Terminal.app window will open with the command

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New snippet |
| `Ctrl+C` | Copy command to clipboard |
| `Ctrl+E` | Execute command |
| `F5` | Refresh snippet list |
| `Ctrl+Enter` | Save (in edit dialog) |

## 📁 Project Structure

```
my_snippet_app/
├── main.py                 # Application entry point
├── config.py               # Application configuration
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── run.sh                 # Run script
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── db/                    # Database layer
│   ├── __init__.py
│   ├── database.py        # SQLite operations
│   └── models.py          # Snippet data model
├── ui/                    # User interface layer
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── snippet_dialog.py  # Create/edit dialog
│   └── ui_forms/          # Qt Designer forms
├── core/                  # Business logic layer
│   ├── __init__.py
│   └── snippet_manager.py # Snippet operations manager
├── assets/                # Static resources
├── data/                  # Database storage
└── tests/                 # Unit tests
    ├── __init__.py
    ├── conftest.py         # Test configuration and fixtures
    ├── test_models.py      # Snippet model tests
    ├── test_database.py    # Database operations tests
    └── test_snippet_manager.py  # Business logic tests
```

## 💡 Usage Examples

### Typical Use Cases

**1. AWS commands with aws-vault:**
```bash
# Name: AWS S3 List Production
# Description: List S3 buckets in production environment
# Command: aws-vault exec production -- aws s3 ls
# Tags: aws, s3, production
```

**2. SSH connections with tunnels:**
```bash
# Name: SSH Tunnel Database
# Description: SSH tunnel to access staging database
# Command: ssh -L 5432:db-internal:5432 user@bastion.staging.company.com
# Tags: ssh, database, staging, tunnel
```

**3. Kubernetes commands:**
```bash
# Name: K8s Production Context
# Description: Switch to production Kubernetes context
# Command: kubectl config use-context production-cluster
# Tags: kubernetes, k8s, production, context
```

**4. Frontend Development:**
```bash
# Name: Start React Dev Server
# Description: Start development server with specific variables
# Command: REACT_APP_ENV=development yarn start
# Tags: react, frontend, development, yarn
```

## 🧪 Testing

The application includes a comprehensive test suite that verifies all core functionality:

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests with verbose output
python -m pytest tests/ -v

# Run tests with coverage report
python -m pytest tests/ --cov=./ --cov-report=term-missing
```

### Test Structure

- **Model Tests** (`test_models.py`):
  - Snippet object creation and validation
  - Data conversion (to/from dict)
  - Tags handling
  - String representations

- **Database Tests** (`test_database.py`):
  - CRUD operations
  - Duplicate name handling
  - Search and filtering
  - Timestamp management

- **Business Logic Tests** (`test_snippet_manager.py`):
  - Input validation
  - Error handling
  - Snippet operations
  - Tag management

### Key Test Cases

1. **Snippet Creation**:
   - Basic snippet creation
   - All fields populated
   - Validation of required fields
   - Handling of duplicate names

2. **Data Integrity**:
   - Proper storage and retrieval
   - No data loss on updates
   - Correct timestamp handling
   - Safe deletion operations

3. **Search and Filtering**:
   - Text search across all fields
   - Tag-based filtering
   - Combined search criteria
   - Results ordering

4. **Error Handling**:
   - Invalid input validation
   - Database operation failures
   - Non-existent snippet operations
   - Duplicate handling

## 🔧 Advanced Configuration

### Database

The application uses SQLite and automatically creates the database at `data/snippets.db`. The database includes:

- `snippets` table with fields:
  - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `name`: TEXT NOT NULL (multiple snippets can have the same name)
  - `description`: TEXT
  - `command_text`: TEXT NOT NULL
  - `tags`: TEXT
  - `last_used`: DATETIME DEFAULT CURRENT_TIMESTAMP
  - `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- Automatic indexes for efficient searches
- Support for duplicate snippet names
- Automatic backup on each execution (future)

### Customization

You can modify the configuration in `config.py`:

```python
# Change database location
DB_PATH = "custom/path/snippets.db"

# Change application name
APP_NAME = "My Command Manager"
```

## 🐛 Troubleshooting

### Common Issues

**1. Error executing commands:**
- Verify that Terminal.app is installed and accessible
- Some complex commands may require additional shell configuration

**2. Dependency errors:**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

**3. Database errors:**
- Delete the `data/snippets.db` file to reset the database
- The application will automatically recreate the tables

**4. Permission issues:**
```bash
# Ensure correct permissions
chmod +x setup.sh run.sh
```

### Logs and Debugging

The application includes a comprehensive logging system that writes to both console and rotating log files:

#### Log Locations
- **Console Output**: Basic operational information and errors
- **Log Files**: Detailed debug information in `logs/snippets_YYYYMMDD.log`
  - Files rotate automatically (max 10MB per file)
  - Keeps last 5 log files
  - Includes timestamps and source locations

#### Log Levels
- **DEBUG**: Detailed information, query parameters, function calls
- **INFO**: General operational events
- **WARNING**: Non-critical issues
- **ERROR**: Operation failures that can be recovered
- **CRITICAL**: Application-breaking errors

#### Example Log Output
```
2024-03-21 10:15:30,123 - main - INFO - Starting Command Snippet Manager application
2024-03-21 10:15:30,234 - db.database - DEBUG - Attempting to connect to database at: data/snippets.db
2024-03-21 10:15:30,345 - db.database - INFO - Successfully connected to database
2024-03-21 10:15:30,456 - db.database - DEBUG - Executing query: INSERT INTO snippets (...) with params: (...)
```

#### Debugging Features
- Full SQL query logging with parameters
- Database operation tracing
- UI event tracking
- Exception stack traces
- Performance metrics

#### Running with Debug Output
```bash
source venv/bin/activate
python -u main.py  # Logs will be in logs/snippets_YYYYMMDD.log
```

#### Analyzing Logs
```bash
# View latest log file
tail -f logs/snippets_$(date +%Y%m%d).log

# Search for errors
grep "ERROR" logs/snippets_*.log

# Follow database operations
grep "db.database" logs/snippets_$(date +%Y%m%d).log
```

## 🔄 Backup and Restore

### Create Backup

Your database is located at `data/snippets.db`. To back up:

```bash
# Copy database
cp data/snippets.db backup/snippets_$(date +%Y%m%d).db

# Or export as JSON (future)
python utils/export_snippets.py > backup/snippets.json
```

### Restore

```bash
# Restore from backup
cp backup/snippets_20250717.db data/snippets.db
```

## 🚀 Future Features

- [ ] Export/Import snippets in JSON format
- [ ] Support for iTerm2 in addition to Terminal.app
- [ ] Categories and subcategories for snippets
- [ ] Execution history
- [ ] Snippets with variables/parameters
- [ ] Password manager integration
- [ ] Dark/light mode
- [ ] Cloud synchronization (optional)

## 📄 License

This project is open source. You can use, modify, and distribute it according to your needs.

## 🤝 Contributing

Contributions are welcome. To contribute:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📞 Support

If you encounter issues or have suggestions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing issues
3. Create a new issue with problem details

---

**Enjoy managing your commands more efficiently! 🎉**
