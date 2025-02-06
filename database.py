import sqlite3

def init_db():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    
    # Create habits table with target value
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            target_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY,
            habit_id INTEGER,
            value REAL,
            date DATE,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    ''')
    
    conn.commit()
    conn.close() 