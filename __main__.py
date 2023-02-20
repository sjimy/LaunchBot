import sys
from app import app

if __name__ == '__main__':
    start_type = 0
    if len(sys.argv) > 1:
        start_type = int(sys.argv[1])
    app.start(start_type)
