from sqlalchemy import create_engine
try:
    engine = create_engine("postgresql://postgres:pradeepan5525@localhost:5432/sales_db")
    with engine.connect() as conn:
        print("Success")
except Exception as e:
    print(f"Error: {e}")
