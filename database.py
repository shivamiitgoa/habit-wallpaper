import sqlite3

def init_db():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    
    # Drop existing tables to update schema
    c.execute("DROP TABLE IF EXISTS habit_logs")
    c.execute("DROP TABLE IF EXISTS habits")
    
    # Create habits table with default_value
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            target_value REAL,
            default_value REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create logs table with unique constraint
    c.execute('''
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY,
            habit_id INTEGER,
            value REAL,
            date DATE,
            FOREIGN KEY (habit_id) REFERENCES habits (id),
            UNIQUE(habit_id, date)  -- Ensure one log per habit per day
        )
    ''')
    
    conn.commit()
    conn.close() 