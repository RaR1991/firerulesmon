# Firewall Rule Management and Visualization Tool

This web-based application provides a modern, theme-aware interface to help engineers and security teams organize, document, search, and audit firewall rules efficiently.


## 🗂️ Core Features

- **Interactive Dashboard**: Get a high-level overview of your firewall rules with statistics on total, active, and disabled rules, as well as rules modified recently. Visualize rule compositions with charts for actions, interfaces, and protocols.
- **Advanced Rules Explorer**: A powerful table view for all firewall rules with:
    - **Live Search & Filtering**: Quickly find rules with a general search or use advanced filters for source, destination, port, protocol, tags, and more.
    - **Customizable Table**: Drag and drop columns to reorder them and use the "Customize" menu to toggle their visibility. Your preferences are saved locally.
    - **Pagination**: The table is fully paginated, and you can choose how many rules to display per page (10, 25, 50, or 100).
    - **Sorting**: All columns are sortable.
    - **Data Export**: Export the currently filtered rules to CSV or JSON format.
- **Detailed Rule View**: Click on any rule to see its full details, including metadata (creation/modification dates and users), associated tickets, tags, notes, and a complete change log.
- **CRUD Operations**: Create, read, update, and delete rules through intuitive forms. All changes are logged to maintain a clear audit trail.
- **Role-Based Access Control (RBAC)**:
    - **Admin**: Full control over all rules and user management (promote, demote, delete users).
    - **Editor**: Can create and edit rules.
    - **Viewer**: Read-only access to rules.
- **Theme-Aware UI**: Toggle between light and dark themes. The application remembers your choice.

## 📦 Tech Stack

- **Backend**: Python 3.x with Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5 with Jinja2 templates
- **Styling**: TailwindCSS
- **Charts**: Chart.js
- **Migrations**: Flask-Migrate with Alembic

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- Python 3.10 or higher
- `pip` for package management

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\activate
      ```
    - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize and upgrade the database:**
    This will create the `instance/site.db` file and set up the necessary tables.
    ```bash
    flask db upgrade
    ```

5.  **Seed the database with initial data (optional but recommended):**
    This script will populate the database with sample users and a large set of realistic firewall rules to demonstrate the application's features.
    ```bash
    python seed_db.py
    ```
    - **Default Users:**
        - `admin` (password: `admin`) - Role: ADMIN
        - `editor` (password: `editor`) - Role: EDITOR
        - `viewer` (password: `viewer`) - Role: VIEWER

6.  **Run the application:**
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

## 💡 Potential Improvements

This project is functionally complete, but there are several areas where it could be enhanced:

- **Advanced Search Syntax**: Implement support for operators like `AND`, `OR`, and `NOT`.
- **Bulk Actions**: Allow admins/editors to select multiple rules and perform bulk operations (e.g., activate, deactivate, delete).
- **API Endpoints**: Develop a RESTful API for programmatic rule management.
- **Automated Testing**: Introduce a test suite with `pytest` to ensure code quality and prevent regressions.
- **Asynchronous Tasks**: Use a task queue like Celery for long-running operations like data imports/exports.

For a full list of potential improvements, see the `current_state.txt` file.

---

*This project was developed with the assistance of Google's Gemini Code Assist.*
