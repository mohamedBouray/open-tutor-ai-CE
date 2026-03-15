import shutil
import os
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime
from fastapi.responses import JSONResponse
from open_webui.utils.auth import get_current_user, timedelta, get_verified_user
from open_webui.internal.db import engine, get_db
from sqlalchemy import func
from open_tutorai.models.database import Classe, Enrollment, Base, StudentActivity
from open_webui.models.users import Users
from sqlalchemy.orm import Session, joinedload, sessionmaker

log = logging.getLogger(__name__)
log.setLevel("INFO")

router = APIRouter()

#########################  To use the get_verified_user function, a parameter (teacher) must be added to the function .
#  /user/miniconda3/envs/tutorai-env/lib/site-packages/open_webui/utils/auth.py
##################################################################################


# --- Pydantic Models ---
class ClasseCreateRequest(BaseModel):
    name: str
    course: Optional[str] = None


class ClasseResponse(BaseModel):
    id: str
    name: str
    course: Optional[str] = None
    user_id: str
    student_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AddStudentRequest(BaseModel):
    name: str
    email: str
    classId: str


# --- Database Session ---


def get_db_session():
    """Get a database session using the same engine as OpenWebUI"""
    Session = sessionmaker(bind=engine)
    return Session()


# --- Classe Endpoints ---
# get all classes for the current user (teacher) - no role check, just return classes where user_id matches
@router.get("/all", response_model=List[ClasseResponse])
async def list_classes(user=Depends(get_current_user)):
    """
    Get list of classes for the current user (No role check)
    """
    session = get_db_session()
    try:
        classes = (
            session.query(Classe)
            .filter(Classe.user_id == user.id)
            .order_by(Classe.created_at.desc())
            .all()
        )

        return classes
    except Exception as e:
        log.error(f"Error listing classes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get classes: {str(e)}")
    finally:
        session.close()


# create a new class
@router.post("/create", response_model=ClasseResponse)
async def create_classe(
    classe_data: ClasseCreateRequest, user=Depends(get_verified_user)
):
    """
    Create a new Classe (No role check)
    """

    print(f"DEBUG: User {user.id} is trying to create a class")
    session = get_db_session()
    try:
        classe_id = str(uuid.uuid4())

        new_classe = Classe(
            id=classe_id,
            name=classe_data.name,
            course=classe_data.course,
            user_id=user.id,
            student_count=0,
            created_at=datetime.now(),
            # updated_at=datetime.now()
        )

        session.add(new_classe)
        session.commit()
        session.refresh(new_classe)

        log.info(f"Classe created: {classe_id} by user {user.id}")
        return new_classe

    except Exception as e:
        session.rollback()
        log.error(f"Error creating classe: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create classe: {str(e)}"
        )
    finally:
        session.close()


# -------- Get Classe By ID --------
@router.get("/{classe_id}", response_model=ClasseResponse)
async def get_classe_by_id(classe_id: str, user=Depends(get_current_user)):
    """
    Get specific classe details (No role check)
    """
    session = get_db_session()
    try:
        classe = (
            session.query(Classe)
            .filter(Classe.id == classe_id, Classe.user_id == user.id)
            .first()
        )

        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")

        return classe
    finally:
        session.close()


@router.patch("/{classe_id}", response_model=ClasseResponse)
async def update_classe(
    classe_id: str, classe_data: ClasseCreateRequest, user=Depends(get_current_user)
):
    """
    Update an existing classe (No role check)
    """
    session = get_db_session()
    try:
        classe = (
            session.query(Classe)
            .filter(Classe.id == classe_id, Classe.user_id == user.id)
            .first()
        )

        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")

        classe.name = classe_data.name
        classe.course = classe_data.course
        # classe.updated_at = datetime.now()

        session.commit()
        session.refresh(classe)
        return classe
    except Exception as e:
        log.error(f"Error updating classe: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update classe")
    finally:
        session.close()


@router.delete("/{classe_id}")
async def delete_classe(classe_id: str, user=Depends(get_current_user)):
    """
    Delete a classe
    """
    session = get_db_session()
    try:
        classe = (
            session.query(Classe)
            .filter(Classe.id == classe_id, Classe.user_id == user.id)
            .first()
        )

        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")

        # delete class folder
        class_folder = f"data/uploads/classes/{classe_id}"

        if os.path.exists(class_folder):
            shutil.rmtree(class_folder)

        session.delete(classe)
        session.commit()

        return JSONResponse(
            content={"status": "success", "message": "Classe deleted successfully"}
        )
    except Exception as e:
        log.error(f"Error deleting classe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        session.close()


############### Enrollment Endpoints ###############
# add a student to a class by email (search for user by email, check if they are a student, and enroll them)
@router.post("/add-student")
async def add_student_to_classe(
    payload: AddStudentRequest, user=Depends(get_current_user)
):
    """
    Search for a user by email, check if they are a student, and enroll them.
    """
    session = get_db_session()
    try:
        target_user = Users.get_user_by_email(payload.email)
        if not target_user:
            raise HTTPException(
                status_code=404, detail="This email is not registered in the System."
            )

        if target_user.role != "user":
            raise HTTPException(
                status_code=400,
                detail=f"User is a {target_user.role}. Only students can be added to the class.",
            )

        classe = (
            session.query(Classe)
            .filter(Classe.id == payload.classId, Classe.user_id == user.id)
            .first()
        )

        if not classe:
            raise HTTPException(
                status_code=403, detail="You don't have access to this class."
            )

        existing = (
            session.query(Enrollment)
            .filter(
                Enrollment.user_id == target_user.id,
                Enrollment.classe_id == payload.classId,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400, detail="Student is already in this class."
            )

        enrollment_id = str(uuid.uuid4())
        new_enrollment = Enrollment(
            id=enrollment_id,
            user_id=target_user.id,
            classe_id=payload.classId,
            points=0,
            grade=0.0,
            notes="",
            created_at=datetime.now(),
        )

        classe.student_count += 1

        session.add(new_enrollment)
        session.commit()

        log.info(f"User {target_user.id} added to class {payload.classId} by {user.id}")

        return {
            "status": "success",
            "message": f"Student {target_user.name} added successfully",
            "student": {
                "id": target_user.id,
                "name": target_user.name,
                "email": target_user.email,
                "points": 0,
                "grade": 0.0,
                "notes": "",
            },
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        session.rollback()
        log.error(f"Error adding student: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# get students in a class with their points and grades, ordered by points desc
@router.get("/{classe_id}/students")
async def get_students_by_class_id(classe_id: str, user=Depends(get_current_user)):
    """Get students in a class with their points and grades, ordered by points desc"""
    session = get_db_session()
    try:
        classe = (
            session.query(Classe)
            .filter(Classe.id == classe_id, Classe.user_id == user.id)
            .first()
        )

        if not classe:
            raise HTTPException(
                status_code=403, detail="you don't have access to this class."
            )

        enrollments = (
            session.query(Enrollment)
            .options(joinedload(Enrollment.user))
            .filter(Enrollment.classe_id == classe_id)
            .order_by(Enrollment.points.desc())
            .all()
        )

        return enrollments
    except Exception as e:
        log.error(f"Error leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


class UpdateGradeRequest(BaseModel):
    grade: float
    notes: Optional[str] = None


@router.patch("/{classe_id}/students/{user_id}/grade")
async def update_student_grade(
    classe_id: str,
    user_id: str,
    payload: UpdateGradeRequest,
    user=Depends(get_current_user),
):
    session = get_db_session()
    try:
        classe = (
            session.query(Classe)
            .filter(Classe.id == classe_id, Classe.user_id == user.id)
            .first()
        )
        if not classe:
            raise HTTPException(status_code=403, detail="Access denied")

        enrollment = (
            session.query(Enrollment)
            .filter(Enrollment.classe_id == classe_id, Enrollment.user_id == user_id)
            .first()
        )

        if not enrollment:
            raise HTTPException(
                status_code=404, detail="Student not found in this class"
            )

        enrollment.grade = payload.grade
        enrollment.notes = payload.notes
        session.commit()
        return {"status": "success", "message": "Grade updated"}
    finally:
        session.close()


################## Dashboard Stats Endpoint ##################
@router.get("/teacher/statistics")
async def get_teacher_stats(
    classe_id: Optional[str] = None, current_user=Depends(get_current_user)
):
    session = get_db_session()
    try:
        query_enrollments = (
            session.query(Enrollment)
            .join(Classe)
            .filter(Classe.user_id == current_user.id)
        )

        if classe_id and classe_id != "undefined" and classe_id != "":
            query_enrollments = query_enrollments.filter(Classe.id == classe_id)

        total_students = query_enrollments.count()
        engaged_students = query_enrollments.filter(Enrollment.points > 0).count()
        engagement_score = (
            round((engaged_students / total_students) * 100)
            if total_students > 0
            else 0
        )
        avg_grade_val = (
            session.query(func.avg(Enrollment.grade))
            .join(Classe)
            .filter(Classe.user_id == current_user.id)
        )

        if classe_id and classe_id != "undefined" and classe_id != "":
            avg_grade_val = avg_grade_val.filter(Classe.id == classe_id)

        success_rate = avg_grade_val.scalar() or 0

        # ---------------------------------------------------------
        #  DYNAMIC CHARTS & TRENDS LOGIC
        # ---------------------------------------------------------
        today = datetime.now()

        last_7_days = [(today - timedelta(days=i)).date() for i in range(6, -1, -1)]
        prev_7_days = [(today - timedelta(days=i)).date() for i in range(13, 6, -1)]

        labels = [d.strftime("%a") for d in last_7_days]

        fourteen_days_ago = today - timedelta(days=14)
        query_activities = (
            session.query(StudentActivity)
            .join(Classe)
            .filter(
                Classe.user_id == current_user.id,
                StudentActivity.created_at >= fourteen_days_ago,
            )
        )

        if classe_id and classe_id != "undefined" and classe_id != "":
            query_activities = query_activities.filter(
                StudentActivity.classe_id == classe_id
            )

        activities = query_activities.all()

        weekly_active = [0] * 7
        previous_weekly = [0] * 7
        engagement_trend = [0] * 7
        prev_engagement = 0

        for act in activities:
            act_date = act.created_at.date()
            if act_date in last_7_days:
                index = last_7_days.index(act_date)
                weekly_active[index] += 1
                engagement_trend[index] += act.points_earned
            elif act_date in prev_7_days:
                index = prev_7_days.index(act_date)
                previous_weekly[index] += 1
                prev_engagement += act.points_earned

        def calc_trend(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 1)

        current_active_total = sum(weekly_active)
        prev_active_total = sum(previous_weekly)
        current_eng_total = sum(engagement_trend)

        active_trend = calc_trend(current_active_total, prev_active_total)
        eng_trend = calc_trend(current_eng_total, prev_engagement)

        success_trend = 0.0 if success_rate == 0 else round(success_rate * 0.05, 1)

        return {
            "stats": {
                "activeStudents": int(total_students),
                "successRate": round(float(success_rate), 1),
                "aiResponseRate": 0,
                "engagement": engagement_score,
            },
            "trends": {
                "activeStudents": active_trend,
                "successRate": success_trend,
                "aiResponseRate": 0,
                "engagement": eng_trend,
            },
            "charts": {
                "labels": labels,
                "weeklyActive": weekly_active,
                "previousWeekly": previous_weekly,
                "engagementTrend": engagement_trend,
            },
        }
    except Exception as e:
        log.error(f"Backend Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        session.close()
