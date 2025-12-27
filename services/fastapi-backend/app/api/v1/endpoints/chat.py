"""Chat completion endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.requests import ChatCompletionRequest
from app.models.responses import ChatCompletionResponse, ErrorResponse
from app.services.genai_service import genai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/completions",
    response_model=ChatCompletionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def chat_completion(request: ChatCompletionRequest) -> ChatCompletionResponse:
    """Generate a chat completion.
    
    Args:
        request: Chat completion request with messages and parameters
        
    Returns:
        Chat completion response
        
    Raises:
        HTTPException: If completion fails
    """
    try:
        if request.stream:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Streaming not supported yet. Use stream=false.",
            )
        
        if not request.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Messages cannot be empty",
            )
        
        result = await genai_service.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            top_k=request.top_k,
        )
        
        return ChatCompletionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

