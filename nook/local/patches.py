"""
Lambda関数をローカルで動作するようにパッチを適用するモジュール
"""

from typing import Any, Dict, TypeVar

from nook.local.storage import local_storage

# 型変数
T = TypeVar("T")


def patch_s3_client() -> None:
    """
    boto3のS3クライアントをパッチして、ローカルストレージを使用するようにする
    """
    import boto3
    from botocore.exceptions import ClientError

    # オリジナルのクライアント生成関数を保存
    original_client = boto3.client

    def patched_client(service_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        S3クライアントの場合はモックを返し、それ以外は元の関数を呼び出す
        """
        if service_name == "s3":
            print(
                "ローカルストレージパッチが適用されました: S3クライアントをモックに置き換えます"
            )

            # S3クライアントのモックを作成
            class MockS3Client:
                def put_object(
                    self, Bucket: str, Key: str, Body: Any
                ) -> Dict[str, Any]:
                    """
                    S3のput_objectをモック
                    """
                    print(f"ローカルストレージに保存: {Key}")
                    local_storage.put_object(Key, Body)
                    return {"ETag": "mock-etag"}

                def get_object(self, Bucket: str, Key: str) -> Dict[str, Any]:
                    """
                    S3のget_objectをモック
                    """
                    try:
                        return local_storage.get_object(Key)
                    except FileNotFoundError:
                        # S3のNoSuchKeyエラーと同様の例外を発生させる
                        error_response = {
                            "Error": {
                                "Code": "NoSuchKey",
                                "Message": "The specified key does not exist.",
                            }
                        }
                        raise ClientError(error_response, "GetObject")

                def list_objects_v2(
                    self, Bucket: str, Prefix: str = ""
                ) -> Dict[str, Any]:
                    """
                    S3のlist_objects_v2をモック
                    """
                    objects = local_storage.list_objects(Prefix)
                    return {"Contents": objects} if objects else {"Contents": []}

                def delete_object(self, Bucket: str, Key: str) -> Dict[str, Any]:
                    """
                    S3のdelete_objectをモック
                    """
                    local_storage.delete_object(Key)
                    return {}

            return MockS3Client()
        else:
            # それ以外のサービスは元の関数を呼び出す
            return original_client(service_name, *args, **kwargs)

    # boto3.clientを置き換え
    boto3.client = patched_client
    print("boto3.clientパッチが適用されました")


def apply_patches() -> None:
    """
    すべてのパッチを適用
    """
    patch_s3_client()
