# User Feedback for Datadog LLMObs - Implementation Plan

**Status**: 📋 Planning  
**Target Date**: TBD  
**Priority**: High

## Overview

This document outlines the plan to implement user feedback collection in the Next.js frontend that integrates with Datadog LLM Observability (LLMObs). This will allow users to rate and comment on AI-generated content (vote extractions, blog posts, images, etc.), providing valuable evaluation data for model performance monitoring.

## Goals

### Primary Goals
1. ✅ Enable users to submit feedback (ratings + comments) for LLM-generated content
2. ✅ Associate feedback with specific LLM spans in Datadog LLMObs
3. ✅ Provide intuitive UI components for feedback collection
4. ✅ Track feedback metrics in Datadog for model evaluation

### Secondary Goals
1. ✅ Support multiple feedback types (thumbs up/down, star ratings, free-form comments)
2. ✅ Enable feedback on different features (vote extraction, content creator, image generation)
3. ✅ Provide feedback history and analytics
4. ✅ Support batch feedback for multi-step workflows

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Feedback UI Components                                 │ │
│  │  - FeedbackButton (thumbs up/down)                     │ │
│  │  - StarRating (1-5 stars)                              │ │
│  │  - CommentBox (free-form text)                         │ │
│  │  - FeedbackModal (combined interface)                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Feedback API Client (/lib/api/feedback.ts)            │ │
│  │  - submitFeedback(spanId, traceId, rating, comment)   │ │
│  │  - getFeedbackHistory()                                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTP POST
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Feedback Endpoint (/api/v1/feedback)                  │ │
│  │  - POST /feedback/submit                               │ │
│  │  - GET /feedback/history                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LLMObs Evaluation Service                             │ │
│  │  - LLMObs.submit_evaluation()                          │ │
│  │  - Format feedback as custom evaluation                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Datadog LLM Observability                       │
│  - Evaluations attached to spans                            │
│  - Metrics: user_rating, user_satisfaction                  │
│  - Tags: feedback_type, comment, feature                    │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Capture Span Context in Frontend

When displaying LLM-generated content, capture and store the span/trace context:

```typescript
interface LLMResponse {
  content: string;
  spanId: string;      // From backend response
  traceId: string;     // From backend response
  mlApp: string;       // Application name (e.g., "vote-extraction-app")
  timestamp: number;   // Response timestamp
}
```

### 2. User Submits Feedback

User interacts with feedback UI:
- Clicks thumbs up/down
- Rates with stars (1-5)
- Adds optional comment

### 3. Frontend Sends Feedback to Backend

```typescript
POST /api/v1/feedback/submit
{
  "span_id": "abc123...",
  "trace_id": "xyz789...",
  "ml_app": "vote-extraction-app",
  "feedback_type": "rating",
  "rating": 5,
  "comment": "Excellent extraction accuracy!",
  "feature": "vote-extraction",
  "user_id": "user123"
}
```

### 4. Backend Submits to Datadog LLMObs

Backend calls `LLMObs.submit_evaluation()`:

```python
LLMObs.submit_evaluation(
    span_context={"span_id": span_id, "trace_id": trace_id},
    ml_app=ml_app,
    label="user_rating",
    metric_type="score",
    value=rating,
    tags={
        "comment": comment,
        "feature": feature,
        "user_id": user_id,
        "feedback_type": feedback_type
    }
)
```

### 5. View in Datadog

Feedback appears in Datadog LLMObs:
- Attached to the specific span
- Visible in trace details
- Aggregated in metrics/dashboards

## Implementation Steps

### Phase 1: Backend API (Week 1)

#### Step 1.1: Create Feedback Models

**File**: `services/fastapi-backend/app/models/feedback.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class FeedbackRequest(BaseModel):
    """User feedback submission request."""
    span_id: str = Field(..., description="Span ID from LLMObs trace")
    trace_id: str = Field(..., description="Trace ID from LLMObs trace")
    ml_app: str = Field(..., description="ML application name")
    feature: str = Field(..., description="Feature name (vote-extraction, content-creator, etc.)")
    
    # Feedback content
    feedback_type: Literal["rating", "thumbs", "comment"] = Field(..., description="Type of feedback")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Star rating (1-5)")
    thumbs: Optional[Literal["up", "down"]] = Field(None, description="Thumbs up/down")
    comment: Optional[str] = Field(None, max_length=1000, description="User comment")
    
    # User context
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")

class FeedbackResponse(BaseModel):
    """Feedback submission response."""
    success: bool
    evaluation_id: Optional[str] = None
    message: str
```

#### Step 1.2: Create Feedback Service

**File**: `services/fastapi-backend/app/services/feedback_service.py`

```python
from ddtrace.llmobs import LLMObs
import logging

logger = logging.getLogger(__name__)

class FeedbackService:
    """Service for submitting user feedback to Datadog LLMObs."""
    
    def __init__(self):
        self._llmobs_enabled = self._check_llmobs()
    
    def _check_llmobs(self) -> bool:
        """Check if LLMObs is available and enabled."""
        try:
            from ddtrace.llmobs import LLMObs
            return True
        except ImportError:
            return False
    
    async def submit_feedback(
        self,
        feedback: FeedbackRequest
    ) -> FeedbackResponse:
        """
        Submit user feedback as a custom evaluation to Datadog LLMObs.
        
        Args:
            feedback: User feedback request
            
        Returns:
            Feedback submission response
        """
        if not self._llmobs_enabled:
            return FeedbackResponse(
                success=False,
                message="LLMObs not available"
            )
        
        try:
            # Prepare span context
            span_context = {
                "span_id": feedback.span_id,
                "trace_id": feedback.trace_id
            }
            
            # Determine metric type and value
            if feedback.feedback_type == "rating" and feedback.rating:
                metric_type = "score"
                value = feedback.rating
                label = "user_rating"
            elif feedback.feedback_type == "thumbs" and feedback.thumbs:
                metric_type = "categorical"
                value = feedback.thumbs
                label = "user_thumbs"
            elif feedback.feedback_type == "comment":
                metric_type = "categorical"
                value = "comment_provided"
                label = "user_comment"
            else:
                return FeedbackResponse(
                    success=False,
                    message="Invalid feedback type or missing value"
                )
            
            # Prepare tags
            tags = {
                "feature": feedback.feature,
                "feedback_type": feedback.feedback_type
            }
            
            if feedback.comment:
                tags["comment"] = feedback.comment
            
            if feedback.user_id:
                tags["user_id"] = feedback.user_id
            
            if feedback.session_id:
                tags["session_id"] = feedback.session_id
            
            # Submit evaluation
            LLMObs.submit_evaluation(
                span_context=span_context,
                ml_app=feedback.ml_app,
                label=label,
                metric_type=metric_type,
                value=value,
                tags=tags
            )
            
            logger.info(
                f"Submitted feedback: {feedback.feedback_type} for "
                f"span {feedback.span_id} in {feedback.ml_app}"
            )
            
            return FeedbackResponse(
                success=True,
                message="Feedback submitted successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}", exc_info=True)
            return FeedbackResponse(
                success=False,
                message=f"Failed to submit feedback: {str(e)}"
            )

# Global service instance
feedback_service = FeedbackService()
```

#### Step 1.3: Create Feedback Endpoint

**File**: `services/fastapi-backend/app/api/v1/endpoints/feedback.py`

```python
from fastapi import APIRouter, HTTPException
from app.models.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import feedback_service

router = APIRouter()

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback for LLM-generated content.
    
    This endpoint accepts user feedback (ratings, thumbs, comments) and
    submits it as a custom evaluation to Datadog LLMObs, associating it
    with the specific span and trace.
    """
    result = await feedback_service.submit_feedback(feedback)
    
    if not result.success:
        raise HTTPException(status_code=500, detail=result.message)
    
    return result
```

#### Step 1.4: Register Feedback Router

**File**: `services/fastapi-backend/app/api/v1/endpoints/__init__.py`

Add:
```python
from app.api.v1.endpoints import feedback
```

**File**: `services/fastapi-backend/app/api/v1/router.py`

Add:
```python
from app.api.v1.endpoints import feedback

api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
```

#### Step 1.5: Update Backend Responses to Include Span Context

Modify existing endpoints to return span/trace IDs:

**Example for Vote Extraction**:

```python
# services/fastapi-backend/app/api/v1/endpoints/vote_extraction.py

@router.post("/extract", response_model=VoteExtractionResponse)
async def extract_votes(...):
    # ... existing code ...
    
    # After extraction, capture span context
    span_context = None
    if DDTRACE_AVAILABLE:
        try:
            from ddtrace import tracer
            span = tracer.current_span()
            if span:
                span_context = {
                    "span_id": str(span.span_id),
                    "trace_id": str(span.trace_id)
                }
        except Exception as e:
            logger.warning(f"Failed to get span context: {e}")
    
    return VoteExtractionResponse(
        data=result,
        span_context=span_context,  # Add to response
        # ... other fields ...
    )
```

### Phase 2: Frontend UI Components (Week 2)

#### Step 2.1: Create Feedback UI Components

**File**: `frontend/nextjs/components/feedback/FeedbackButton.tsx`

```typescript
'use client';

import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FeedbackButtonProps {
  spanId: string;
  traceId: string;
  mlApp: string;
  feature: string;
  onFeedbackSubmit?: (success: boolean) => void;
}

export function FeedbackButton({
  spanId,
  traceId,
  mlApp,
  feature,
  onFeedbackSubmit
}: FeedbackButtonProps) {
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFeedback = async (thumbs: 'up' | 'down') => {
    setIsSubmitting(true);
    setFeedback(thumbs);

    try {
      const response = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          span_id: spanId,
          trace_id: traceId,
          ml_app: mlApp,
          feature: feature,
          feedback_type: 'thumbs',
          thumbs: thumbs,
        }),
      });

      const result = await response.json();
      onFeedbackSubmit?.(result.success);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      onFeedbackSubmit?.(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleFeedback('up')}
        disabled={isSubmitting || feedback !== null}
        className={feedback === 'up' ? 'bg-green-100' : ''}
      >
        <ThumbsUp className="w-4 h-4" />
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleFeedback('down')}
        disabled={isSubmitting || feedback !== null}
        className={feedback === 'down' ? 'bg-red-100' : ''}
      >
        <ThumbsDown className="w-4 h-4" />
      </Button>
    </div>
  );
}
```

**File**: `frontend/nextjs/components/feedback/StarRating.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Star } from 'lucide-react';

interface StarRatingProps {
  spanId: string;
  traceId: string;
  mlApp: string;
  feature: string;
  onRatingSubmit?: (rating: number, success: boolean) => void;
}

export function StarRating({
  spanId,
  traceId,
  mlApp,
  feature,
  onRatingSubmit
}: StarRatingProps) {
  const [rating, setRating] = useState<number>(0);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRating = async (value: number) => {
    setIsSubmitting(true);
    setRating(value);

    try {
      const response = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          span_id: spanId,
          trace_id: traceId,
          ml_app: mlApp,
          feature: feature,
          feedback_type: 'rating',
          rating: value,
        }),
      });

      const result = await response.json();
      onRatingSubmit?.(value, result.success);
    } catch (error) {
      console.error('Failed to submit rating:', error);
      onRatingSubmit?.(value, false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => handleRating(star)}
          onMouseEnter={() => setHoverRating(star)}
          onMouseLeave={() => setHoverRating(0)}
          disabled={isSubmitting || rating > 0}
          className="transition-colors disabled:cursor-not-allowed"
        >
          <Star
            className={`w-6 h-6 ${
              (hoverRating || rating) >= star
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            }`}
          />
        </button>
      ))}
    </div>
  );
}
```

**File**: `frontend/nextjs/components/feedback/FeedbackModal.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { StarRating } from './StarRating';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  spanId: string;
  traceId: string;
  mlApp: string;
  feature: string;
  title?: string;
}

export function FeedbackModal({
  isOpen,
  onClose,
  spanId,
  traceId,
  mlApp,
  feature,
  title = 'Rate this response'
}: FeedbackModalProps) {
  const [rating, setRating] = useState<number>(0);
  const [comment, setComment] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) return;

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          span_id: spanId,
          trace_id: traceId,
          ml_app: mlApp,
          feature: feature,
          feedback_type: 'rating',
          rating: rating,
          comment: comment || undefined,
        }),
      });

      if (response.ok) {
        onClose();
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Rating</label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  className="transition-colors"
                >
                  <Star
                    className={`w-8 h-8 ${
                      rating >= star
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">
              Comment (optional)
            </label>
            <Textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Tell us what you think..."
              rows={4}
              maxLength={1000}
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={rating === 0 || isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

#### Step 2.2: Create Feedback API Client

**File**: `frontend/nextjs/lib/api/feedback.ts`

```typescript
export interface FeedbackSubmission {
  span_id: string;
  trace_id: string;
  ml_app: string;
  feature: string;
  feedback_type: 'rating' | 'thumbs' | 'comment';
  rating?: number;
  thumbs?: 'up' | 'down';
  comment?: string;
  user_id?: string;
  session_id?: string;
}

export interface FeedbackResponse {
  success: boolean;
  evaluation_id?: string;
  message: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const feedbackApi = {
  /**
   * Submit user feedback for an LLM span
   */
  submitFeedback: async (feedback: FeedbackSubmission): Promise<FeedbackResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/feedback/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedback),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit feedback: ${response.statusText}`);
    }

    return response.json();
  },
};
```

### Phase 3: Integration with Existing Features (Week 3)

#### Step 3.1: Vote Extraction Integration

**File**: `frontend/streamlit/pages/1_🗳️_Vote_Extractor.py`

Add feedback buttons after displaying extraction results:

```python
import streamlit as st

# After displaying results
if st.session_state.get('extraction_result'):
    result = st.session_state['extraction_result']
    
    # Display results...
    
    # Add feedback section
    st.divider()
    st.subheader("📊 Rate this extraction")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        rating = st.slider(
            "How accurate was the extraction?",
            min_value=1,
            max_value=5,
            value=3,
            key="extraction_rating"
        )
    
    with col2:
        if st.button("Submit Rating"):
            if 'span_id' in result and 'trace_id' in result:
                # Submit feedback
                feedback_data = {
                    "span_id": result['span_id'],
                    "trace_id": result['trace_id'],
                    "ml_app": "vote-extraction-app",
                    "feature": "vote-extraction",
                    "feedback_type": "rating",
                    "rating": rating
                }
                # Make API call...
                st.success("Thank you for your feedback!")
            else:
                st.error("Unable to submit feedback: trace information not available")
```

#### Step 3.2: Content Creator Integration

Add feedback button to Next.js Content Creator:

```typescript
// frontend/nextjs/app/content-creator/page.tsx

import { FeedbackButton } from '@/components/feedback/FeedbackButton';

// In the response display section
{response && spanContext && (
  <div className="mt-4">
    <FeedbackButton
      spanId={spanContext.span_id}
      traceId={spanContext.trace_id}
      mlApp="content-creator-app"
      feature="content-creator"
      onFeedbackSubmit={(success) => {
        if (success) {
          toast.success('Thank you for your feedback!');
        }
      }}
    />
  </div>
)}
```

#### Step 3.3: Image Creator Integration

Add feedback to image generation results:

```typescript
// frontend/nextjs/app/image-creator/page.tsx

import { StarRating } from '@/components/feedback/StarRating';

// After displaying generated image
{generatedImage && spanContext && (
  <div className="mt-4 flex items-center gap-4">
    <span className="text-sm text-gray-600">Rate this image:</span>
    <StarRating
      spanId={spanContext.span_id}
      traceId={spanContext.trace_id}
      mlApp="image-creator-app"
      feature="image-generation"
      onRatingSubmit={(rating, success) => {
        if (success) {
          console.log(`Image rated: ${rating} stars`);
        }
      }}
    />
  </div>
)}
```

### Phase 4: Analytics & Monitoring (Week 4)

#### Step 4.1: Create Datadog Dashboard

Create a custom dashboard in Datadog to visualize user feedback:

**Widgets to include**:
1. **Average Rating by Feature** (timeseries)
   - Query: `avg:llmobs.evaluation.user_rating{*} by {feature}`

2. **Thumbs Up/Down Distribution** (pie chart)
   - Query: `count:llmobs.evaluation.user_thumbs{*} by {value}`

3. **Feedback Volume** (timeseries)
   - Query: `count:llmobs.evaluation.user_rating{*}`

4. **Negative Feedback Alerts** (threshold)
   - Query: `avg:llmobs.evaluation.user_rating{*}`
   - Alert when < 3.0

5. **Recent Comments** (log stream)
   - Filter: `@tags.comment:*`

#### Step 4.2: Set Up Monitors

Create Datadog monitors for feedback quality:

```yaml
# Monitor: Low User Satisfaction
Query: avg(last_1h):avg:llmobs.evaluation.user_rating{feature:vote-extraction} < 2.5
Message: |
  User satisfaction for {{feature.name}} has dropped below 2.5 stars
  Current average: {{value}}
  
  Action items:
  - Review recent comments for issues
  - Check for model degradation
  - Investigate recent changes
```

#### Step 4.3: Feedback Analytics Endpoint

**File**: `services/fastapi-backend/app/api/v1/endpoints/feedback.py`

Add analytics endpoint:

```python
@router.get("/analytics")
async def get_feedback_analytics(
    feature: Optional[str] = None,
    days: int = 7
):
    """
    Get feedback analytics for specified period.
    
    Returns aggregated feedback metrics:
    - Average rating by feature
    - Total feedback count
    - Thumbs up/down ratio
    - Recent comments
    """
    # Query Datadog API for feedback metrics
    # Return aggregated statistics
    pass
```

## Testing Strategy

### Unit Tests

**File**: `services/fastapi-backend/tests/test_feedback_service.py`

```python
import pytest
from app.services.feedback_service import FeedbackService
from app.models.feedback import FeedbackRequest

@pytest.mark.asyncio
async def test_submit_rating_feedback():
    service = FeedbackService()
    
    feedback = FeedbackRequest(
        span_id="test_span_123",
        trace_id="test_trace_456",
        ml_app="test-app",
        feature="test-feature",
        feedback_type="rating",
        rating=5
    )
    
    result = await service.submit_feedback(feedback)
    assert result.success is True

@pytest.mark.asyncio
async def test_submit_thumbs_feedback():
    service = FeedbackService()
    
    feedback = FeedbackRequest(
        span_id="test_span_123",
        trace_id="test_trace_456",
        ml_app="test-app",
        feature="test-feature",
        feedback_type="thumbs",
        thumbs="up"
    )
    
    result = await service.submit_feedback(feedback)
    assert result.success is True
```

### Integration Tests

Test end-to-end flow:

```python
import pytest
from fastapi.testclient import TestClient

def test_feedback_submission_endpoint(client: TestClient):
    response = client.post("/api/v1/feedback/submit", json={
        "span_id": "test_span_123",
        "trace_id": "test_trace_456",
        "ml_app": "test-app",
        "feature": "test-feature",
        "feedback_type": "rating",
        "rating": 4,
        "comment": "Great accuracy!"
    })
    
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### Frontend Tests

**File**: `frontend/nextjs/__tests__/components/FeedbackButton.test.tsx`

```typescript
import { render, fireEvent, waitFor } from '@testing-library/react';
import { FeedbackButton } from '@/components/feedback/FeedbackButton';

describe('FeedbackButton', () => {
  it('submits thumbs up feedback', async () => {
    const onFeedbackSubmit = jest.fn();
    
    const { getByRole } = render(
      <FeedbackButton
        spanId="test_span"
        traceId="test_trace"
        mlApp="test-app"
        feature="test-feature"
        onFeedbackSubmit={onFeedbackSubmit}
      />
    );
    
    const thumbsUpButton = getByRole('button', { name: /thumbs up/i });
    fireEvent.click(thumbsUpButton);
    
    await waitFor(() => {
      expect(onFeedbackSubmit).toHaveBeenCalledWith(true);
    });
  });
});
```

## Security Considerations

### 1. Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/submit")
@limiter.limit("10/minute")
async def submit_feedback(feedback: FeedbackRequest):
    # ... implementation ...
```

### 2. Input Validation

- Validate span_id and trace_id formats
- Sanitize comment text (remove HTML, scripts)
- Limit comment length (max 1000 characters)

### 3. Authentication

Optionally require authentication:

```python
from fastapi import Depends
from app.core.auth import get_current_user

@router.post("/submit")
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: User = Depends(get_current_user)
):
    feedback.user_id = current_user.id
    # ... implementation ...
```

## Rollout Plan

### Week 1: Backend Development
- ✅ Create feedback models and service
- ✅ Implement feedback endpoint
- ✅ Update existing endpoints to return span context
- ✅ Write unit tests

### Week 2: Frontend Components
- ✅ Create feedback UI components
- ✅ Implement feedback API client
- ✅ Write component tests

### Week 3: Feature Integration
- ✅ Integrate with Vote Extraction
- ✅ Integrate with Content Creator
- ✅ Integrate with Image Creator
- ✅ End-to-end testing

### Week 4: Analytics & Launch
- ✅ Create Datadog dashboard
- ✅ Set up monitors and alerts
- ✅ User documentation
- ✅ Soft launch and monitoring

## Success Metrics

### Adoption Metrics
- Feedback submission rate (target: >20% of sessions)
- Average feedback per user (target: >2 per session)
- Feedback completion time (target: <30 seconds)

### Quality Metrics
- Average rating by feature (target: >4.0 stars)
- Thumbs up ratio (target: >80%)
- Comment quality (manual review sample)

### Technical Metrics
- API response time (target: <200ms p95)
- Feedback submission success rate (target: >99%)
- Datadog evaluation ingestion rate

## Future Enhancements

### Phase 2 Features
1. **Comparative Feedback**: Allow users to compare two outputs
2. **Batch Feedback**: Rate multiple extractions at once
3. **Feedback History**: Show user's past feedback
4. **Feedback Analytics Dashboard**: Embedded analytics in frontend
5. **A/B Testing Integration**: Track feedback by experiment variant

### Advanced Features
1. **Automated Feedback Collection**: Trigger feedback prompts based on confidence scores
2. **Feedback-driven Retraining**: Use feedback to create training datasets
3. **Sentiment Analysis**: Analyze comment sentiment automatically
4. **Feedback Aggregation**: Show aggregated ratings to users

## Related Documentation

- **[Datadog LLMObs - Submit Evaluations](https://docs.datadoghq.com/llm_observability/evaluations/submit_evaluations/)** - Official guide
- **[docs/features/VOTE_EXTRACTION_LLMOBS_SPANS.md](./VOTE_EXTRACTION_LLMOBS_SPANS.md)** - Existing LLMObs implementation
- **[guides/llmobs/sources/01_INSTRUMENTING_SPANS.md](../../guides/llmobs/sources/01_INSTRUMENTING_SPANS.md)** - Span instrumentation guide

## Appendix: Example Queries

### Datadog Query Examples

**Average rating by feature (last 24h)**:
```
avg:llmobs.evaluation.user_rating{*} by {feature}
```

**Feedback volume over time**:
```
count:llmobs.evaluation.user_rating{*}.as_count()
```

**Low ratings alert**:
```
avg(last_4h):avg:llmobs.evaluation.user_rating{feature:vote-extraction} < 3
```

**Comments with negative sentiment**:
```
@tags.comment:* @evaluation.user_rating:<3
```

---

**Status**: 📋 Ready for Implementation  
**Estimated Effort**: 4 weeks  
**Dependencies**: Existing LLMObs instrumentation

