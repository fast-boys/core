from fastapi import HTTPException, Request


async def get_internal_id(request: Request):
    internal_id = request.headers.get("INTERNAL_ID_HEADER")
    if not internal_id:
        return "asdf"
        # raise HTTPException(status_code=400, detail="Internal ID not provided")
    return internal_id
