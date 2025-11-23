from db.db import get_session
from db.models import Job, ApplicationPackage
from sqlalchemy import delete

def main():
    # The ID used in scripts/test_insert.py
    SAMPLE_JOB_ID = "manual_test_1"
    
    with get_session() as session:
        print(f"Attempting to remove job: {SAMPLE_JOB_ID}")
        
        # 1. Delete any associated application packages first
        pkg_stmt = delete(ApplicationPackage).where(ApplicationPackage.job_id == SAMPLE_JOB_ID)
        pkg_result = session.execute(pkg_stmt)
        
        # 2. Delete the job itself
        job_stmt = delete(Job).where(Job.id == SAMPLE_JOB_ID)
        job_result = session.execute(job_stmt)
        
        session.commit()
        
        if job_result.rowcount > 0:
            print(f"Successfully deleted sample job.")
            print(f"Also removed {pkg_result.rowcount} associated application package(s).")
        else:
            print("Sample job not found in database.")

if __name__ == "__main__":
    main()
