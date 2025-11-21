from db.db import get_session
from db.models import Job


def main():
    s = get_session()
    # simple existence check
    j = Job(
        id="manual_test_1",
        source="manual",
        title="Sample",
        company="ExampleCo",
        description="Test description",
        location="Remote",
        remote_flag=True,
    )
    s.add(j)
    s.commit()
    count = s.query(Job).count()
    print(f"Jobs count after insert: {count}")


if __name__ == "__main__":
    main()
