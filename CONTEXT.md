# Project Context for LLM

## 1. Project Summary
**Name**: Command Snippet Manager (CmdSnips)  
**Purpose**: Desktop GUI application to store, search, copy and execute command snippets with rich tagging and search capabilities.  
**Stack**: Python 3.13, PyQt6, SQLite  
**Latest Version**: 1.3.2 (see VERSION file)  
**Repository**: https://github.com/ColinBurgess/CommandSnippetManager

## 2. Architecture Overview

### Layers
- **UI Layer**: PyQt6 widgets with modern dark theme
  - `ui/main_window.py` — Main window, table/card views, search filtering, toolbar actions
  - `ui/snippet_dialog.py` — Add/edit snippet dialog with focus styling (drop-shadow)
  - `ui/modern_widgets.py` — Custom widgets (TagBadgeWidget for colored tags, SnippetCard for card view)
  - `ui/modern_dark_theme.py` — Centralized QSS stylesheet, colors, selection/focus styling

- **Business Logic Layer**: Snippet management
  - `core/snippet_manager.py` — High-level operations (add, update, find, record_usage, get_tags_list)

- **Data Layer**: Persistence
  - `db/database.py` — SQLite interface, CRUD operations, parameterized search queries
  - `db/models.py` — Snippet dataclass (id, name, description, command_text, tags, last_used, created_at)

- **Utilities**: Supporting functions
  - `utils.py` — Clipboard operations (copy_to_clipboard), terminal execution (execute_in_terminal_macos)
  - `logs/interaction_events.log` — Event logging for diagnostics (runtime, gitignored)

### Key Data Flows

**1. Search Flow**
```
User types in search_edit 
  → filter_snippets() normalizes input ('*' → '%')
  → database.search_snippets(term) uses LIKE queries
  → updates table/card view with results
  → preserves selection ID if snippet still in results
```

**2. Add/Edit Flow**
```
User clicks New/Edit 
  → SnippetDialog opens with 4 input fields (name, description, command_text, tags)
  → SnippetDialog validates on save
  → SnippetManager.add_snippet() or update_snippet() calls database
  → load_snippets() reloads table/cards after commit
```

**3. Execute Flow**
```
User selects snippet, clicks Execute
  → get_selected_snippet_text() retrieves command from table
  → execute_in_terminal_macos(command) opens Terminal.app
  → SnippetManager.record_usage(snippet_id) updates last_used timestamp
```

**4. Copy Flow**
```
User selects snippet, clicks Copy
  → copy_to_clipboard(command_text) copies to system clipboard
  → No UI reload (preserves selection and prevents reordering)
```

## 3. File Structure
```
CmdSnips/
├── main.py                          # Entry point; initializes QApplication, DB, UI
├── VERSION                          # Current version (1.3.2)
├── CHANGELOG.md                     # Version history with commit summaries
├── CONTEXT.md                       # This file (LLM context initialization)
├── README.md                        # User-facing documentation
├── run.sh                           # Shell script to run app
├── requirements.txt                 # Python dependencies (PyQt6, etc.)
│
├── core/
│   ├── __init__.py
│   └── snippet_manager.py           # Business logic; manages snippet lifecycle
│
├── db/
│   ├── __init__.py
│   ├── database.py                  # SQLite interface; CRUD, search, tags
│   ├── models.py                    # Snippet dataclass
│   └── migrations.py                # Future schema migrations
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # Main UI; table, toolbar, search, preview
│   ├── snippet_dialog.py            # Dialog for add/edit; validated inputs
│   ├── modern_widgets.py            # TagBadgeWidget, SnippetCard, ModernFrame
│   ├── modern_dark_theme.py         # QSS stylesheet, centralized styling
│   ├── backup_dialog.py             # Backup/restore UI
│   └── ui_forms/                    # (placeholder for future form layouts)
│
├── utils/
│   ├── __init__.py
│   ├── backup.py                    # Database backup/restore utilities
│   ├── clipboard.py                 # Clipboard operations
│   └── logger.py                    # Logging configuration
│
├── utils.py                         # Top-level utils (clipboard, terminal exec)
│
├── tests/
│   ├── conftest.py                  # Pytest fixtures (temp DB, SnippetManager, sample data)
│   ├── test_database.py             # DB CRUD, search, tags, timestamp tests
│   ├── test_models.py               # Snippet model validation, dict conversion
│   └── test_snippet_manager.py      # Manager logic, validation, usage recording
│
├── logs/                            # Runtime logs (gitignored)
│   └── interaction_events.log       # Event log for diagnostics
│
└── data/
    ├── snippets.db                  # SQLite database
    └── snippets_backup_*.db         # Backup snapshots
```

## 4. Snippet Model
```python
# db/models.py - Snippet dataclass
class Snippet:
    id: int | None = None              # Auto-generated primary key
    name: str                          # Required; must be non-empty
    description: str = ""              # Optional; rich text description
    command_text: str                  # Required; the command to execute
    tags: str = ""                     # Comma-separated tags (e.g., "python, script")
    last_used: datetime                # Timestamp of last execution
    created_at: datetime               # Creation timestamp
    
    # Methods:
    # - to_dict() / from_dict(): serialize/deserialize
    # - get_tags_list(): parse tags string into list, trimmed
    # - __str__() / __repr__(): string representation
```

## 5. Search & Filtering

### Search Behavior
- **Default**: LIKE '%term%' across name, description, command_text, and tags.
- **Wildcard**: User types `*` in search → UI converts to `%` before query.
- **Example**: User searches `aws*` → query finds "aws ecr login", "aws iam login", etc.
- **Selection preservation**: When filter results change, app keeps the same snippet selected (if still visible).

### Query Example
```sql
SELECT * FROM snippets
WHERE (name LIKE ? OR description LIKE ? OR command_text LIKE ? OR tags LIKE ?)
AND (tags LIKE ? OR ? = '')  -- optional tag filter
ORDER BY last_used DESC, name ASC
```

## 6. UI Details

### Main Window
- **Toolbar**: Refresh, New, Copy, Execute, Card View (toggle button), Backup buttons.
- **Search Box**: QLineEdit with objectName='search_edit', clear button, live filtering.
- **Command Preview**: QTextEdit with objectName='command_edit', shows selected snippet command, selectable/copyable.
- **Table/Card View**: Toggle between QTableWidget (table view) and QListWidget (card view).
- **No Menu Bar**: Actions available only via toolbar buttons (menu bar hidden).

### Theme & Styling
- **Color Scheme**: Dark modern theme (dark gray background, light text, blue accents).
- **Selection**: High-contrast blue for selected rows and text in QLineEdit/QTextEdit.
- **Focus**: Drop-shadow effect on dialog fields for visual feedback.
- **Tags**: Colored badge widgets (deterministic color by tag hash).
- **Description**: Sanitized to remove zero-width/soft-hyphen characters before display.

### Dialog Fields (Add/Edit)
1. **Name** (QLineEdit): Required; no duplicates allowed (unless explicitly permitted).
2. **Description** (QTextEdit): Optional; rich text or plain text.
3. **Command** (QLineEdit): Required; the shell command to execute.
4. **Tags** (QLineEdit): Optional; comma-separated (e.g., "aws, cli, iam").

All 4 fields have consistent focus styling (inline QSS + drop-shadow).

## 7. Recent Key Changes (v1.3.0+)

### v1.3.2
- Selection visibility in QLineEdit/QTextEdit with objectName-based QSS rules.
- Wildcard mapping: user input `*` → SQL `%` in search.
- Selection preservation across filtering (maintains selected snippet ID).

### v1.3.1
- Removed in-window menu bar (actions available via toolbar).
- Tag badge sizing fixes (deterministic width/height, elide long tags).
- Fixed description text rendering on hover (no weight/color change).

### v1.3.0
- Added visible Card View toggle button (synchronized with toolbar QAction).
- Preserved selection when filtering snippets.
- Sanitized descriptions to remove invisible characters (zero-width, soft-hyphen).

### v1.2.0
- Focus visuals: inline QSS + drop-shadow effect on dialog fields.
- Consistent theme rules for selection/hover across widgets.

## 8. Testing

### Current Coverage
- **Unit Tests**: 32 passing (pytest -q)
- **Test Suites**:
  - `test_database.py` — CRUD operations, search, tags, timestamps (14 tests)
  - `test_models.py` — Snippet validation, dict conversion, tag parsing (10 tests)
  - `test_snippet_manager.py` — Manager logic, validation, usage recording (8 tests)

### Test Infrastructure
- **Fixtures** (conftest.py):
  - `temp_db_path` — temporary SQLite file
  - `database` — Database instance connected to temp DB
  - `snippet_manager` — SnippetManager instance
  - `sample_snippet_data` — dict with test snippet fields

### Known Coverage Gaps
- **UI Tests**: No pytest-qt tests yet; would test QLineEdit selection, QTextEdit styling, table interactions.
- **Integration Tests**: No end-to-end tests combining UI + DB.
- **Edge Cases**: Unicode/emoji tags, very long descriptions, concurrent DB access.

### Running Tests
```bash
pytest tests/ -q                    # Run all tests, quiet output
pytest tests/ -v                    # Verbose output
pytest tests/test_database.py -v    # Single file
pytest --cov                        # With coverage report
```

## 9. Development Workflow

### Running the App
```bash
./run.sh                            # Start app
python main.py                      # Alternative: direct Python
```

### Code Style
```bash
black ui/ core/ db/ utils.py        # Format with Black
flake8 ui/ core/ db/ utils.py       # Lint (if configured)
```

### Git Workflow (Conventional Commits)
```bash
git add .
git commit -m "feat(ui): add feature" # or fix, chore, docs, style, refactor, test
git push origin main
```

### Version & Release
- Edit `VERSION` file with new version (e.g., "1.3.3").
- Update `CHANGELOG.md` with changes.
- Commit: `git commit -m "chore(release): bump to v1.3.3"`
- Push: `git push origin main`

## 10. Key Guardrails for LLM

1. **Database Compatibility**: Maintain backward compatibility with existing `snippets.db` schema.
2. **Testing**: UI changes must pass `pytest tests/ -q` without errors.
3. **Documentation**: Update `CHANGELOG.md` and `VERSION` when merging features.
4. **Commit Style**: Use conventional commits (feat, fix, chore, docs).
5. **Logging**: Preserve event logging in `logs/interaction_events.log` for diagnostics.
6. **No Hardcoded Secrets**: Use environment variables or config files for credentials.
7. **Platform**: macOS-first (Terminal.app integration); cross-platform fallback for utilities.
8. **UI Consistency**: All dialog fields use same focus styling; selection always visible.
9. **Selection Preservation**: Don't reset selection on operations (copy, filter) to maintain UX stability.

## 11. Known Limitations & TODOs

### Current Limitations
- SQLite file-based; no multi-user concurrency support.
- QLineEdit selection styling may vary on non-macOS platforms.
- Card View layout not optimized for very large snippet collections (1000+).
- Terminal execution is macOS-specific (osascript); other platforms use subprocess.
- No export/import feature (data locked in SQLite).

### Future Enhancements
- [ ] Multi-user sync (cloud backend, conflict resolution).
- [ ] Snippet versioning (git-like history per snippet).
- [ ] Browser extension for quick snippet insertion.
- [ ] Custom tag hierarchy / filtering by tag groups.
- [ ] Performance: render tags via QStyledItemDelegate (not individual widgets).
- [ ] Cross-platform terminal integration (Windows, Linux).
- [ ] Search suggestions / autocomplete from tags.

## 12. Quick Commands & Troubleshooting

### Running & Debugging
```bash
python main.py                      # Run app with console output
./run.sh                            # Run app (redirects output to log)
pytest tests/ -v                    # Run tests with verbose output
tail -f logs/interaction_events.log # Watch event log in real-time
```

### Common Issues
- **No snippets showing**: Check `data/snippets.db` exists; run `python main.py` to initialize.
- **Selection not visible**: Verify QSS rules in `ui/modern_dark_theme.py` for `#command_edit`, `#search_edit`.
- **Tests failing**: Run `pytest tests/ -v` to see which test(s) failed; check database.py query syntax.
- **Terminal execution fails**: Ensure Terminal.app is installed; check `execute_in_terminal_macos()` in utils.py.

### Database Reset
```bash
rm data/snippets.db                 # Delete database (will recreate on app start)
python main.py                      # Reinitialize
```

### View/Clear Logs
```bash
cat logs/interaction_events.log     # View event log
> logs/interaction_events.log       # Clear log file
```

## 13. Dependencies

### Core Dependencies
- **PyQt6**: GUI framework
- **sqlite3**: Built-in Python; database
- **subprocess**: Built-in Python; command execution
- **logging**: Built-in Python; event logging

### Dev Dependencies (optional)
- **pytest**: Unit testing
- **pytest-qt** (planned): UI testing with Qt
- **black**: Code formatting
- **flake8**: Linting (optional)

### Install
```bash
pip install -r requirements.txt     # Install core deps
```

## 14. Contact & Ownership

**Maintainer**: Colin Moreno Burgess  
**Repository**: https://github.com/ColinBurgess/CommandSnippetManager  
**Issues/PRs**: See GitHub issue tracker for bugs and feature requests.

---

**Last Updated**: November 3, 2025 (v1.3.2)  
**For LLM Context Initialization**: Copy the entire contents of this file into the initial chat/context to avoid rescanning the repository.
