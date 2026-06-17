# main.py
# Author  : William
# Version : 1.1
#
# Application entry point. Run this file to start ExpenseTracker.
# Usage: python main.py
#
# On first run, if no database file exists, the database is created
# and seeded automatically before the GUI launches.
# Subsequent runs skip setup and go straight to the login screen.

import os
import sys

# Ensure the project root is on sys.path so all module imports resolve
# correctly regardless of where Python is invoked from.
# Done before any internal imports so the path is guaranteed when they run.
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def main() -> None:
    """
    Entry point. Initialises the database if needed then launches the GUI.
    Exits with a clear error message if setup or launch fails.
    """
    # Import DB_PATH inside main() — not at module level.
    # Module-level imports run before sys.path is confirmed on some
    # execution environments, causing ModuleNotFoundError.
    from database.db_connect import DB_PATH

    # Ensure the directory that will hold the database file exists.
    # SQLite cannot create a .db file inside a directory that does not exist.
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # First-run database setup
    if not os.path.exists(DB_PATH):
        print("Database not found. Running first-time setup...")
        try:
            import setup_db
            setup_db.create_tables()
            setup_db.seed_data()
            print("Setup complete.")
        except Exception as e:
            # If setup fails at any point, remove the partial database so
            # the next run triggers setup again from a clean state.
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            print(f"Setup failed: {e}")
            print("The application cannot start. Check the error above.")
            sys.exit(1)

    # Import App after setup is confirmed — deferred to avoid initialising
    # the Tkinter display before the database is guaranteed to be ready.
    try:
        from gui.app import App
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()