"""
ローカルWebサーバーを実装するモジュール
"""

import os
import pathlib
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from nook.local.storage import local_storage
from nook.local.runner import import_lambda_module


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを作成

    Returns
    -------
    FastAPI
        FastAPIアプリケーション
    """
    # viewerモジュールをインポート
    viewer_module = import_lambda_module("viewer")

    # テンプレートディレクトリのパスを正しく設定
    lambda_dir = pathlib.Path(__file__).parent.parent.parent / "nook" / "lambda"
    templates_dir = lambda_dir / "viewer" / "templates"

    # 新しいJinja2Templatesインスタンスを作成して置き換え
    viewer_module.templates = Jinja2Templates(directory=str(templates_dir))

    # viewerモジュールのFastAPIアプリを取得
    app = viewer_module.app

    # S3クライアントをモック
    def mock_s3_client_get_object(Bucket: str, Key: str) -> Dict[str, Any]:
        """
        S3のget_objectをモック

        Parameters
        ----------
        Bucket : str
            バケット名
        Key : str
            キー

        Returns
        -------
        Dict[str, Any]
            S3のレスポンス
        """
        try:
            return local_storage.get_object(Key)
        except FileNotFoundError:
            # S3のNoSuchKeyエラーと同様の例外を発生させる
            from botocore.exceptions import ClientError

            error_response = {
                "Error": {
                    "Code": "NoSuchKey",
                    "Message": "The specified key does not exist.",
                }
            }
            raise ClientError(error_response, "GetObject")

    def mock_s3_client_list_objects_v2(Bucket: str, Prefix: str) -> Dict[str, Any]:
        """
        S3のlist_objects_v2をモック

        Parameters
        ----------
        Bucket : str
            バケット名
        Prefix : str
            プレフィックス

        Returns
        -------
        Dict[str, Any]
            S3のレスポンス
        """
        objects = local_storage.list_objects(Prefix)
        return {"Contents": objects}

    # S3クライアントのメソッドをモック
    viewer_module.s3_client.get_object = mock_s3_client_get_object
    viewer_module.s3_client.list_objects_v2 = mock_s3_client_list_objects_v2

    return app


def start_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """
    Webサーバーを起動

    Parameters
    ----------
    host : str, optional
        ホスト, by default "127.0.0.1"
    port : int, optional
        ポート, by default 8000
    """
    # 環境変数を設定
    os.environ["LOCAL_STORAGE"] = "true"
    os.environ["BUCKET_NAME"] = "local-bucket"

    # アプリケーションを作成
    app = create_app()

    # サーバーを起動
    print(f"サーバーを起動しています: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
