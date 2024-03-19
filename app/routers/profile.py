router = APIRouter(tags=["user_profile"])


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

http_bearer = HTTPBearer()


@router.get("/profile")
async def read_users_me(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    user = get_user_by_token(request, db, "service_access")
    if not user:
        raise HTTPException(status_code=404, detail="Not found User")
    # 사용자 정보를 직접 반환하거나  객체를 사용해서 반환
    if user.user_type == UserType.Standard:
        encoded_image = None
        file_location = user.profile_picture_url
        if file_location is not None:
            with open(file_location, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        user_data = {
            "email": user.email,
            "name": user.name,
            "profile_picture_url": encoded_image,
            "user_type": user.user_type,
            "auth_provider": user.auth_provider,
        }
        return user_data

    elif user.user_type == UserType.Business:
        business_user = db.query(BusinessUser).filter(BusinessUser.id == user.id).first()
        print(business_user)
        user_data = {
            "email": user.email,
            "name": user.name,
            "user_type": user.user_type,
            "auth_provider": user.auth_provider,
            "company_info": business_user.company_info,
            "company_email": business_user.company_email,
            "company_address": business_user.company_address,
        }
        return user_data
