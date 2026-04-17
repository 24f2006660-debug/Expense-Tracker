# Expense Tracker App

A simple Expense Tracker web application built with Flask and Supabase (PostgreSQL).

## Features

- Add, view, edit, and delete expenses
- Categorize expenses (Food, Transportation, Entertainment, Utilities, Other)
- Store data in Supabase PostgreSQL database

## Setup

1. Create a `.env` file in the project root with your database URL:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.bpwlzgrorjqsmfeksoqf.supabase.co:5432/postgres
   ```
   Replace `YOUR_PASSWORD` with your actual Supabase password.

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and go to `http://127.0.0.1:5000`

## Database

The app connects to a Supabase PostgreSQL database. The database URL is loaded from the `.env` file for security.

## Project Structure

- `app.py`: Main Flask application
- `.env`: Environment variables (not committed to version control)
- `templates/`: HTML templates
  - `index.html`: List all expenses
  - `add.html`: Form to add new expense
  - `edit.html`: Form to edit existing expense
- `requirements.txt`: Python dependencies