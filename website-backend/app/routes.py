from __future__ import annotations

from flask_restful import Api

from app.resources.auth_resources import (
    EmailVerifyResource,
    LoginResource,
    LogoutResource,
    RegisterResource,
    ResetPasswordResource,
)

from app.resources.article_resources import (
    CreateDraftResource,
)


def register_api_resources(api: Api) -> None:
    """在 Flask-RESTful Api 上注册 API 资源。

    Args:
        api: Flask-RESTful Api 实例。
    """

    # 登录类资源
    api.add_resource(RegisterResource,     "/api/auth/register")
    api.add_resource(LoginResource,        "/api/auth/login")
    api.add_resource(LogoutResource,       "/api/auth/logout")
    api.add_resource(EmailVerifyResource,  "/api/auth/email_verifying")
    api.add_resource(ResetPasswordResource, "/api/auth/reset_success")

    # 文章类资源
    api.add_resource(CreateDraftResource, "/api/articles/drafts")

    
