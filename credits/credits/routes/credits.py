from credits.models.models import Credits, CreditsModel
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post(
    "/add_credits",
    response_description="Credits added successfully",
)  # type: ignore
async def add_credits(credits: CreditsModel) -> JSONResponse:
    """
    Add credits to a specific institution. If a institution doesn't exist, then it creates one instance.

    :param credits: Credits info(institution and credits value)
    :type credits: BaseModel(see model.py)
    """
    try:
        added_credits = credits.credits
        institution = credits.institution

        credits_obj = Credits.objects(institution=credits.institution).first()
        if credits_obj:
            credits_obj.credits += added_credits
            credits_obj.save()
        else:
            new_credits = Credits(institution=institution, credits=added_credits)
            new_credits.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": f"{added_credits} credits added successfully to {institution}"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/remove_credits",
    response_description="Credits removed successfully",
)  # type: ignore
async def remove_credits(credits: CreditsModel) -> JSONResponse:
    """
    Removes credits from a specific institution

    :param credits: Credits info(institution and credits value)
    :type credits: BaseModel(see models.py)
    """
    try:
        removed_credits = credits.credits
        institution = credits.institution
        credits_obj = Credits.objects(institution=institution)
        if len(credits_obj) > 0:
            credits_obj = credits_obj.first()
            if credits_obj.credits >= removed_credits:
                credits_obj.credits -= removed_credits
                credits_obj.save()
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Can't remove {removed_credits} amount of credits from {institution} institution",
                )
        else:
            raise HTTPException(
                status_code=404, detail=f"Institution: {institution} not found"
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": f"{removed_credits} successfully removed from {institution}"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/get_credits", response_description="Credits fetched successfully"
)  # type: ignore
async def get_credits(institution: str) -> JSONResponse:
    """
    Returns credits from a specific institution

    :param institution: The institution's name
    :type institution: str
    """
    try:
        credits_obj = Credits.objects(institution=institution).first()
        if credits_obj:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "description": "Credits fetched successfully",
                    "credits": credits_obj.credits,
                },
            )
        else:
            raise HTTPException(
                status_code=404, detail=f"Institution: {institution} not found"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
