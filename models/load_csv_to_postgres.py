import os
import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:123456@postgres:5432/cbo_sinonimos"
)

def load_csv():
    df = pd.read_csv("cbo2002-sinonimo.csv")
    engine = create_engine(DATABASE_URL)
    df.to_sql("cbo_sinonimos", engine, if_exists="append", index=False)
    print("✅ CSV importado com sucesso!")

if __name__ == "__main__":
    load_csv()
