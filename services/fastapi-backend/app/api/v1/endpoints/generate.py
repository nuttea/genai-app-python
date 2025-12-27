"""Text generation endpoints."""

import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.models.requests import GenerateRequest
from app.models.responses import ErrorResponse, GenerateResponse
from app.services.genai_service import genai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post(
    "",
    response_model=GenerateResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_text(request: GenerateRequest) -> GenerateResponse:
    """Generate text from a prompt.

    Args:
        request: Generation request with prompt and parameters

    Returns:
        Generated text response

    Raises:
        HTTPException: If generation fails
    """
    try:
        if request.stream:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Streaming not supported in this endpoint. Use /generate/stream instead.",
            )

        result = await genai_service.generate_text(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            top_k=request.top_k,
            stop_sequences=request.stop_sequences,
        )

        return GenerateResponse(**result)
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/stream")
async def generate_text_stream(request: GenerateRequest) -> StreamingResponse:
    """Stream generated text from a prompt.

    Args:
        request: Generation request with prompt and parameters

    Returns:
        Streaming response with generated text
    """

    async def generate() -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        try:
            async for chunk in genai_service.generate_text_stream(
                prompt=request.prompt,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                top_k=request.top_k,
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Error streaming text: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
