from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
)

import settings
from main.modules.auth.model import AuthUser
from main.modules.jwt.model import TokenBlocklist


class JWTController:
    """
    This class is used to handle all operation related to jwt.
    """

    @classmethod
    def get_user_identity(cls):
        """
        This function is used to get the identity of current logged-in user
        :return:
        """
        return get_jwt_identity()

    @classmethod
    def block_jwt_token(cls):
        token = get_jwt()
        jti = token["jti"]
        ttype = token["type"]
        identity = get_jwt_identity()
        user_id = identity["user_id"]
        TokenBlocklist.create({"jti": jti, "ttype": ttype, "user_id": user_id})

    @classmethod
    def token_revoked_check(cls, jwt_header, jwt_payload: dict) -> TokenBlocklist or None:
        """
        This function is used to check the jwt token  is revoked or not (If it is present in
        the TokenBlocklist then it is revoked.)
        :param jwt_payload:
        :return:
        """
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).scalar()
        return token is not None

    @classmethod
    def get_access_and_refresh_token(cls, auth_user: AuthUser) -> dict:
        """
        This function is used to get the access and refresh token.
        :param auth_user:
        :return:
        """
        identity = {"user_id": auth_user.id}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_in": settings.TOKEN_EXPIRE_IN * 60,
        }

    @classmethod
    def get_access_token_from_refresh_token(cls) -> dict:
        """
        This function is used to get a new access token using refresh token.
        :return:
        """
        access_token = create_access_token(identity=cls.get_user_identity())
        return {"access_token": access_token, "expire_in": 60 * settings.TOKEN_EXPIRE_IN}
