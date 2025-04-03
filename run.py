import os
import sys

# Adicionar o diretório atual ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001) 