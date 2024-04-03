from services.gcs import generate_signed_url

from fastapi import HTTPException, Request


async def get_internal_id(request: Request):
    internal_id = request.headers.get("INTERNAL_ID_HEADER")
    if not internal_id:
        # return "8b5b03b7-ae9f-458e-a2b9-558eac541629"
        raise HTTPException(status_code=400, detail="Internal ID not provided")
    return internal_id


def get_profile_image_signed_url(image_path: str) -> str:
    return generate_signed_url(image_path)
