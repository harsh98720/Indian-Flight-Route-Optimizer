# Indian Flight Route Optimizer & Diversion System (JSON Edition)

A Flask web application for a DAA project. It demonstrates Dijkstra shortest-distance routing, BFS fewest-leg routing, route diversion simulation, and airport/route CRUD.

## Storage

All persistent data is stored in `data/airports.json` and `data/routes.json`. No SQLite, SQLAlchemy, MySQL, or database server is required. Paths are built relative to `app.py`, so the project can run from any extracted folder. The included JSON files contain illustrative sample data (12 airports and 26 routes).

## Run on Windows

1. Install Python 3.10 or newer.
2. Extract this folder and open it in VS Code.
3. In the project directory, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.

4. Open http://127.0.0.1:5000.

## GitHub portability

Commit both JSON files in `data/`; they provide the initial sample network. Do not commit `.venv/` or Python cache files. New edits are saved to those JSON files, so keep in mind that running the app from a read-only folder may prevent saving. Multiple concurrent writers are not recommended for JSON storage.

## Notes

- Airport coordinates and route distances are illustrative project data, not live airline schedules.
- The map uses OpenStreetMap tiles and requires an internet connection to display the map.
- If a user edits sample data, their edits remain on that machine in the JSON files.
