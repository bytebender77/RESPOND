from src.qdrant.client import get_qdrant_client


try:
    client = get_qdrant_client()
    print("Testing query_points...")
    
    # Just check signature by inspection or trying to call it with named args
    # We don't have a valid vector, so it will fail, but we want to know IF it accepts the args
    import inspect
    sig = inspect.signature(client.query_points)
    print(f"Signature: {sig}")
    
except Exception as e:
    print(f"Error: {e}")
