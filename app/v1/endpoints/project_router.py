# app/api/v1/endpoints/project_endpoint.py
from fastapi import APIRouter, HTTPException, FastAPI, Request
from app.domain.project.services import check_project_exists_for_user
from app.domain.user.repository_impl import create_project_for_user
from app.infrastructure.database.neo4j.neo4j_connection import neo4j_conn
from pydantic import BaseModel


router = APIRouter()


@router.get("/")
def get_projects():
    query = "MATCH (projects:Project) RETURN projects"
    try:
        projects = neo4j_conn.query(query)
        print(projects)
        projects = [dict(project['projects']) for project in projects]  # Adjust based on your data structure
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProjectCreateRequest(BaseModel):
    user_id: str
    description: str
    name: str

@router.post("/create/")
def create_project(payload: ProjectCreateRequest):
    try:
        result = create_project_for_user(payload.user_id ,payload.description, payload.name)
        return {"message": "Project created successfully", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Proceed to create the new project in Neo4j and link it under the "Projects" node
    # This part would inv