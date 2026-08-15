"""Convenience entry point for the optional PostgreSQL CSV import."""
from backend.import_data import import_orders

if __name__ == "__main__":
    print(f"Imported {import_orders()} rows into PostgreSQL orders.")
