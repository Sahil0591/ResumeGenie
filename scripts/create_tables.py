from db.db import engine
from db.models import Base


def main():
    Base.metadata.create_all(engine)
    print("Tables created")


if __name__ == "__main__":
    main()
