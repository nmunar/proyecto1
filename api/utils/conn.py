from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(
    'postgresql://postgres:Nikitos99@localhost:5432/concursos',
    convert_unicode=True,
    pool_recycle=3600,
    pool_size=10,
)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
