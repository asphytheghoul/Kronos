import pandas as pd
from sqlalchemy import create_engine
df = pd.read_csv('data/AAPL.csv')
df.columns = [c.lower() for c in df.columns] 

engine = create_engine('postgresql://<host_name>:<password>@localhost:5432/<db_name>')

df.to_sql("my_table_name", engine)