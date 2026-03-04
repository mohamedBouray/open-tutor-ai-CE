from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime
from fastapi.responses import JSONResponse

from open_webui.utils.auth import get_current_user
from open_webui.internal.db import engine
from open_tutorai.models.database import  Assignment , Base
from open_webui.models.users import Users 
from sqlalchemy.orm import sessionmaker

# Setup logging
log = logging.getLogger(__name__)
log.setLevel("INFO")

router = APIRouter()


class AssignmentCreateRequest(BaseModel):

    title : str
    description : str
    classe_id : str
    deadline : datetime
    points : int

class AssignmentResponse(BaseModel):
    id : str
    title :str 
    description : str
    classe_id :str
    user_id : str
    deadline : datetime
    points :int
    status : str
    max_submissions :int
    current_submissions : int


def get_db_session():
    """Get a database session using the same engine as OpenWebUI"""
    Session = sessionmaker(bind=engine)
    return Session()


@router.get("/all", response_model=List[AssignmentResponse])
async def list_Assignment(user=Depends(get_current_user)):
    """
    Get list of assignments for the current user (No role check)
    """
    session = get_db_session()

    try:
        assignment = session.query(Assignment).filter(
            Assignment.user_id == user.id
        ).order_by(Assignment.created_at.desc()).all()
        
        return assignment
    except Exception as e:
        log.error(f"Error listing Assignment: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get Assignment: {str(e)}")
    finally:
        session.close()


@router.post("/create", response_model=AssignmentResponse)
async def create_assignment(assignment_data: AssignmentCreateRequest,user=Depends(get_current_user)):
    """
    Create a new assignment 
    """

    print(f"DEBUG: User {user.id} is trying to create a assignment")
    session = get_db_session()
    try:
        assignment_id = str(uuid.uuid4())
        
        new_assignment = Assignment(
            id=assignment_id,
            title=assignment_data.title,
            description=assignment_data.description,
            classe_id=assignment_data.classe_id,
            user_id=user.id,
            points=assignment_data.points,
            deadline = assignment_data.deadline,
            created_at =datetime.now()
        )
        
        session.add(new_assignment)
        session.commit()
        session.refresh(new_assignment)

        log.info(f"assignment created: {id} by user {user.id}")
        return new_assignment

    except Exception as e:
        session.rollback()
        log.error(f"Error creating assignment: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create assignment: {str(e)}"
        )
    finally:
        session.close()




@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str, 
    assignment_data: AssignmentCreateRequest, 
    user=Depends(get_current_user)
):
    """
    Update an existing assignment
    """
    session = get_db_session()
    try:
        assignment = session.query(Assignment).filter(
            Assignment.id == assignment_id, 
            Assignment.user_id == user.id
        ).first()

        if not assignment:
            raise HTTPException(status_code=404, detail="assignment not found")

        # Update fields
        assignment.title= assignment_data.title
        assignment.description = assignment_data.description
        assignment.classe_id = assignment_data.classe_id
        assignment.deadline = assignment_data.deadline
        assignment.points = assignment_data.points
        assignment.updated_at = datetime.now()

        session.commit()
        session.refresh(assignment)
        return assignment
    except Exception as e:
        log.error(f"Error updating assignment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update assignment")
    finally:
        session.close()


@router.delete("/{assignment_id}")
async def delete_assignment(assignment_id: str, user=Depends(get_current_user)):
    """
    Delete a assignment (No role check)
    """
    session = get_db_session()
    try:
        assignment = session.query(Assignment).filter(
            Assignment.id == assignment_id, 
            Assignment.user_id == user.id
        ).first()
        
        if not assignment:
            raise HTTPException(status_code=404, detail="assignment not found")

        session.delete(assignment)
        session.commit()
        
        return JSONResponse(
            content={"status": "success", "message": "assignment deleted successfully"}
        )
    except Exception as e:
        log.error(f"Error deleting assignment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        session.close()