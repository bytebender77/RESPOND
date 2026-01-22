import sys
import os

# Add local directory to path
sys.path.append(os.getcwd())

from src.qdrant.client import get_qdrant_client
from qdrant_client import QdrantClient

try:
    print(f"QdrantClient file: {sys.modules['qdrant_client'].__file__}")
except:
    pass

try:
    client = get_qdrant_client()
    print(f"Client object: {client}")
    print(f"Client type: {type(client)}")
    
    if hasattr(client, 'search'):
        print("✅ Client has 'search' method")
    else:
        print("❌ Client MISSING 'search' method")
        print("Available attributes:")
        print([d for d in dir(client) if not d.startswith('_')])
        
except Exception as e:
    print(f"Error getting client: {e}")
