from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

# Import with explicit type hints
from ..models.review import Review, ReviewCreate, ReviewReply, ReviewResponse

router = APIRouter()


# --------------------------------------------------
# Submit Review
# --------------------------------------------------
@router.post("/submit_review", response_description="Review submitted successfully", status_code=status.HTTP_201_CREATED)  # type: ignore[misc]
async def submit_review(review: ReviewCreate) -> JSONResponse:

    try:
        # Verify that only one review exists for a student and specific exam
        # Unique (student, course, exam_type, year) tuples in review database
        if Review.objects(
            student_id=review.student_id,
            course_id=review.course_id,
            exam_type=review.exam_type,
            year=review.year,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review already exists for this student and exam",
            )

        new_review = Review(
            student_id=review.student_id,
            course_id=review.course_id,
            exam_type=review.exam_type,
            year=review.year,
            review_text=review.review_text,
        )
        new_review.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": f"Review of student {review.student_id} for (course, exam_type, year) = ({review.course_id}, {review.exam_type}, {review.year}) successfully submitted",
            },
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --------------------------------------------------
# Get Reviews
# --------------------------------------------------
@router.get("/get_reviews", response_description="Reviews extracted successfully")  # type: ignore[misc]
async def get_reviews(
    student_ids: Optional[list[str]] = Query(default=None),
    course_ids: Optional[list[str]] = Query(default=None),
    exam_types: Optional[list[str]] = Query(default=None),
    years: Optional[list[int]] = Query(default=None),
    is_replied: Optional[bool] = Query(default=None),
) -> JSONResponse:

    try:
        query: Dict[str, Any] = {}
        reviews: List[ReviewResponse] = []

        if student_ids is not None:
            query["student_id__in"] = student_ids
        if course_ids is not None:
            query["course_id__in"] = course_ids
        if exam_types is not None:
            query["exam_type__in"] = exam_types
        if years is not None:
            query["year__in"] = years
        if is_replied is not None:
            query["is_replied"] = is_replied

        for single_review in Review.objects(**query):
            reviews.append(
                ReviewResponse(
                    student_id=single_review.student_id,
                    course_id=single_review.course_id,
                    exam_type=single_review.exam_type,
                    year=single_review.year,
                    review_text=single_review.review_text,
                    reply_text=single_review.reply_text,
                    is_replied=single_review.is_replied,
                    created_at=single_review.created_at.isoformat(),
                ).dict()
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": "Reviews extracted successfully",
                "reviews": reviews,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --------------------------------------------------
# Update Review Reply
# --------------------------------------------------
@router.put("/reply", response_description="Reply was successfully submitted")  # type: ignore[misc]
async def update_reply(reply: ReviewReply) -> JSONResponse:

    try:
        review = Review.objects(
            student_id=reply.student_id,
            course_id=reply.course_id,
            exam_type=reply.exam_type,
            year=reply.year,
        ).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

        review.reply_text = reply.reply_text
        review.is_replied = True
        review.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": f"Replied to the Review of student {reply.student_id} for (course, exam_type, year) = ({reply.course_id}, {reply.exam_type}, {reply.year}) successfully",
            },
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
