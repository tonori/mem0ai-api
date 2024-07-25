import logging

import uvicorn
import dotenv

from fastapi import FastAPI, APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typenv import Env
from pydantic import BaseModel
from typing import Dict, Union, List
from dependencies import get_memory_id, MemoryHistory, authorize
from response import SuccessfulResponse, ErrorResponse
from mem0 import Memory
from mem0ai_config import vector_config, llm_config, embedding_config
from errors.exception import UnauthorizedException
from errors.handler import unauthorized_exception_handler, qdrant_client_unexpected_handler
from qdrant_client.http.exceptions import UnexpectedResponse

dotenv.load_dotenv()
env = Env()

mem0 = Memory.from_config({
    "vector_store": vector_config,
    "llm": llm_config,
    "embedder": embedding_config
})

app = FastAPI(
    title="Mem0ai to API"
)

api_router = APIRouter(
    tags=["mem0ai"]
)


class StoreMemoryData(BaseModel):
    data: str
    user_id: Union[str, None] = None
    agent_id: Union[str, None] = None
    run_id: Union[str, None] = None
    metadata: Union[dict, None] = None
    filters: Union[Dict, None] = None
    prompt: Union[str, None] = None


@api_router.get("/authorized", description="Check authorization status")
def authorized(token=Depends(authorize)):
    return SuccessfulResponse()


@api_router.post(
    path="/store",
    description="Create a new memory.",
    response_model=SuccessfulResponse
)
async def store_memory(data: StoreMemoryData, token=Depends(authorize)):
    execute_results = mem0.add(**data.dict())
    return SuccessfulResponse(
        data=execute_results
    )


@api_router.put(
    path="/update/{memory_id}",
    description="Update a memory by ID."
)
async def update_memory(
        data: str,
        memory_id: str = Depends(get_memory_id),
        token=Depends(authorize)
):
    execute_result = mem0.update(
        memory_id=memory_id,
        data=data
    )
    return SuccessfulResponse(
        data=execute_result
    )


class SearchMemoryData(BaseModel):
    query: str
    user_id: Union[str, None] = None
    agent_id: Union[str, None] = None
    run_id: Union[str, None] = None
    limit: Union[int, None] = 100
    filters: Union[dict, None] = None


@api_router.post(
    path="/search",
    description="Search for memories.",
    dependencies=[Depends(authorize)]
)
async def search_memories(
        data: SearchMemoryData
):
    memories = mem0.search(
        **data.dict()
    )
    return SuccessfulResponse(
        data=memories
    )


@api_router.get(
    path="/retrieve",
    description="List all memories.",
    dependencies=[Depends(authorize)]
)
async def retrieve_memories(
        user_id: Union[str, None] = None,
        agent_id: Union[str, None] = None,
        run_id: Union[str, None] = None,
        limit: Union[int, None] = 100
):
    memories = mem0.get_all(
        user_id=user_id,
        agent_id=agent_id,
        run_id=run_id,
        limit=limit
    )

    return SuccessfulResponse(
        data=memories
    )


@api_router.get(
    path="/retrieve/{memory_id}",
    description="Get the history of changes for a memory by ID."
)
async def retrieve_memory(
        memory_id: str = Depends(get_memory_id),
        token=Depends(authorize)
):
    memory = mem0.history(memory_id=memory_id)
    return SuccessfulResponse(
        data=memory
    )


@api_router.delete(
    path="/delete/{memory_id}",
    description="Delete a memory by ID."
)
async def delete_memory(
        memory_id: str = Depends(get_memory_id),
        token=Depends(authorize)
):
    memory_histories: List[MemoryHistory] = mem0.history(memory_id=memory_id)
    if memory_histories[-1].get("is_deleted"):
        return JSONResponse(
            content=ErrorResponse(
                code=status.HTTP_404_NOT_FOUND,
                error="NotFoundError",
                message=f'Memory {memory_id} not found.'
            ).model_dump(),
            status_code=status.HTTP_404_NOT_FOUND
        )

    mem0.delete(
        memory_id=memory_id
    )

    return SuccessfulResponse()


@api_router.delete(
    path="/delete-all",
    description="Delete a memory by ID."
)
async def delete_memory(
        user_id: Union[str, None] = None,
        agent_id: Union[str, None] = None,
        run_id: Union[str, None] = None,
        token=Depends(authorize)
):
    try:
        mem0.delete_all(
            user_id, agent_id, run_id
        )

        return SuccessfulResponse()
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="ValueError",
                message=e
            ),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


@api_router.delete(
    path="/reset-all",
    description="Reset the memory store."
)
async def reset_all_memories(token=Depends(authorize)):
    mem0.reset()
    return JSONResponse(
        content=SuccessfulResponse().model_dump_json(),
        status_code=204
    )


app.include_router(api_router)
app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
app.add_exception_handler(UnexpectedResponse, qdrant_client_unexpected_handler)

if __name__ == "__main__":
    uvicorn.run("app:app",
                host=env.str(name="SERVER_HOST", default="127.0.0.1"),
                port=env.int(name="SERVER_PORT", default=8000),
                reload=True)
