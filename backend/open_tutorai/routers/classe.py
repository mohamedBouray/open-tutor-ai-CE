from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime
from fastapi.responses import JSONResponse

from open_webui.utils.auth import get_current_user
from open_webui.internal.db import engine, get_db
from open_tutorai.models.database import Classe,Assignment, Enrollment, Base
from open_webui.models.users import Users 
from sqlalchemy.orm import Session, joinedload, sessionmaker

# Setup logging
log = logging.getLogger(__name__)
log.setLevel("INFO")

router = APIRouter()

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
    # updated_at=datetime.now()

    class Config:
        from_attributes = True

class AddStudentRequest(BaseModel):
    name:str
    email: str
    classId: str

# --- Database Session ---

def get_db_session():
    """Get a database session using the same engine as OpenWebUI"""
    Session = sessionmaker(bind=engine)
    return Session()



@router.get("/all", response_model=List[ClasseResponse])
async def list_classes(user=Depends(get_current_user)):
    """
    Get list of classes for the current user (No role check)
    """
    session = get_db_session()
    try:
        classes = session.query(Classe).filter(
            Classe.user_id == user.id
        ).order_by(Classe.created_at.desc()).all()
        
        return classes
    except Exception as e:
        log.error(f"Error listing classes: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get classes: {str(e)}"
        )
    finally:
        session.close()


@router.post("/create", response_model=ClasseResponse)
async def create_classe(classe_data: ClasseCreateRequest,user=Depends(get_current_user)):
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
            status_code=500, 
            detail=f"Failed to create classe: {str(e)}"
        )
    finally:
        session.close()



@router.get("/{classe_id}", response_model=ClasseResponse)
async def get_classe_by_id(classe_id: str, user=Depends(get_current_user)):
    """
    Get specific classe details (No role check)
    """
    session = get_db_session()
    try:
        classe = session.query(Classe).filter(
            Classe.id == classe_id, 
            Classe.user_id == user.id
        ).first()

        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")
        
        return classe
    finally:
        session.close()


@router.patch("/{classe_id}", response_model=ClasseResponse)
async def update_classe(
    classe_id: str, 
    classe_data: ClasseCreateRequest, 
    user=Depends(get_current_user)
):
    """
    Update an existing classe (No role check)
    """
    session = get_db_session()
    try:
        classe = session.query(Classe).filter(
            Classe.id == classe_id, 
            Classe.user_id == user.id
        ).first()

        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")

        # Update fields
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
    Delete a classe (No role check)
    """
    session = get_db_session()
    try:
        classe = session.query(Classe).filter(
            Classe.id == classe_id, 
            Classe.user_id == user.id
        ).first()
        
        if not classe:
            raise HTTPException(status_code=404, detail="Classe not found")

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




# Add students 
@router.post("/add-student")
async def add_student_to_classe(
    payload: AddStudentRequest, 
    user=Depends(get_current_user)
):
    """
    Search for a user by email, check if they are a student, and enroll them.
    """
    session = get_db_session()
    try:
        target_user = Users.get_user_by_email(payload.email)
        if not target_user:
            raise HTTPException(
                status_code=404, 
                detail="This email is not registered in the System."
            )
        
        
        if target_user.role != "user":
            raise HTTPException(
                status_code=400, 
                detail=f"User is a {target_user.role}. Only students can be added to the class."
            )

        classe = session.query(Classe).filter(
            Classe.id == payload.classId, 
            Classe.user_id == user.id
        ).first()

        if not classe:
            raise HTTPException(status_code=403, detail="You don't have access to this class.")

        existing = session.query(Enrollment).filter(
            Enrollment.user_id == target_user.id,
            Enrollment.classe_id == payload.classId
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Student is already in this class.")

        enrollment_id = str(uuid.uuid4())
        new_enrollment = Enrollment(
            id=enrollment_id,
            user_id=target_user.id,
            classe_id=payload.classId,
            created_at=datetime.now() 
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
                "email": target_user.email
            }
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        session.rollback()
        log.error(f"Error adding student: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
    finally:
        session.close()


@router.get("/{classe_id}/students")
async def get_students_by_class_id(classe_id: str, user=Depends(get_current_user)):
    """
    Kajibu t-talamid li m-inscrits f had l-class m3a l-points dyalhom
    """
    session = get_db_session()
    try:
        # 1. Check ownership (bach may-choufch ay wahed l-leaderboard)
        classe = session.query(Classe).filter(
            Classe.id == classe_id, 
            Classe.user_id == user.id
        ).first()

        if not classe:
            raise HTTPException(status_code=403, detail="Ma3ndekch l-haq tchouf had l-class")

        # 2. Fetch Enrollments + User info
        enrollments = session.query(Enrollment).options(
            joinedload(Enrollment.user)
        ).filter(
            Enrollment.classe_id == classe_id
        ).order_by(Enrollment.points.desc()).all()

        # 3. Transform data bach t-matching Svelte mapping (en.user.name, etc.)
        return enrollments
        
    except Exception as e:
        log.error(f"Error leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()