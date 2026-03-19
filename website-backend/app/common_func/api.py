from __future__ import annotations

from flask import Flask
from flask_restful import Api

from app.routes import register_api_resources


def create_api(app: Flask) -> Api:
    """创建 Flask-RESTful Api 并注册所有资源。

    Args:
        app: Flask 应用实例。

    Returns:
        Flask-RESTful Api 实例。
    """
    api = Api(app)
    register_api_resources(api)
    return api
