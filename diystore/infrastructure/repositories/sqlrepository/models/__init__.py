from sqlalchemy.orm import declarative_base
from pendulum import timezone

Base = declarative_base()
tz = timezone("UTC")
