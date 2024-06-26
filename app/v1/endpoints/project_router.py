# app/api/v1/endpoints/project_endpoint.py
from fastapi import APIRouter, HTTPException, FastAPI, Request
from app.domain.project.services import fetch_project_hierarchy, fetch_graph_data_for_vis_js
from app.domain.user.repository_impl import create_project_for_user
from app.infrastructure.database.neo4j.neo4j_connection import neo4j_conn
from pydantic import BaseModel

router = APIRouter()

class ProjectReadRequest(BaseModel):
    project_node_id: str | None
    user_id: str
@router.post("/get_project_graph")
async def fetch_graph(payload: ProjectReadRequest):
    project_data = await fetch_graph_data_for_vis_js(payload.project_node_id, payload.user_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_data
@router.post("/get_project_graph_in_readable_format")
async def get_project_graph_in_readable_format(payload: ProjectReadRequest):
    project_data = await fetch_project_hierarchy(payload.project_node_id, payload.user_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_data

class GetProject(BaseModel):
    user_id: str
@router.post("/")
def get_projects(payload: GetProject):

    query = """
    MATCH (user:User {userId: $user_id})-[:HAS_PROJECT]->(projects:Project)
    RETURN projects
    """
    try:
        print("getting projects")
        projects = neo4j_conn.query(query, parameters={'user_id': payload.user_id})
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
