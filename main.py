import sys
from database import init_db
from gui import main as gui_main

def main():
    # Initialize database
    init_db()
    
    # Start GUI
    gui_main()

if __name__ == "__main__":
    main() 