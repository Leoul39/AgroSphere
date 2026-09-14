from sqlalchemy import create_engine

def get_engine(user, password, db, host="localhost", port=5432):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)
