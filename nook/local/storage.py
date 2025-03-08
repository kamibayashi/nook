"""
ローカルファイルシステムをS3の代わりに使用するためのストレージモジュール
"""

import os
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Union


class LocalStorage:
    """
    S3の代わりにローカルファイルシステムを使用するストレージクラス

    Parameters
    ----------w
    base_dir : str
        データを保存するベースディレクトリ
    """

    def __init__(self, base_dir: str = "data"):
        """
        初期化

        Parameters
        ----------
        base_dir : str, optional
            データを保存するベースディレクトリ, by default "data"
        """
        self.base_dir = Path(base_dir)
        self._ensure_base_dir()

    def _ensure_base_dir(self) -> None:
        """ベースディレクトリが存在することを確認"""
        os.makedirs(self.base_dir, exist_ok=True)

    def _ensure_dir_for_key(self, key: str) -> None:
        """キーに対応するディレクトリが存在することを確認"""
        dir_path = self.base_dir / os.path.dirname(key)
        os.makedirs(dir_path, exist_ok=True)

    def put_object(self, key: str, body: Union[str, bytes, Dict, List]) -> None:
        """
        オブジェクトを保存

        Parameters
        ----------
        key : str
            保存先のキー（パス）
        body : Union[str, bytes, Dict, List]
            保存するデータ
        """
        self._ensure_dir_for_key(key)
        file_path = self.base_dir / key

        if isinstance(body, (dict, list)):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(body, f, ensure_ascii=False, indent=2)
        elif isinstance(body, str):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(body)
        elif isinstance(body, bytes):
            with open(file_path, "wb") as f:
                f.write(body)

    def get_object(self, key: str) -> Dict[str, Any]:
        """
        オブジェクトを取得

        Parameters
        ----------
        key : str
            取得するキー（パス）

        Returns
        -------
        Dict[str, Any]
            取得したオブジェクト（S3のレスポンス形式に合わせる）

        Raises
        ------
        FileNotFoundError
            指定されたキーが存在しない場合
        """
        file_path = self.base_dir / key
        if not file_path.exists():
            raise FileNotFoundError(f"Key not found: {key}")

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            # S3のレスポンスと互換性のあるBodyオブジェクトを作成
            class BytesIOWrapper:
                def __init__(self, data):
                    self.data = data
                    self.position = 0

                def read(self, size=None):
                    if size is None:
                        return self.data
                    else:
                        result = self.data[self.position : self.position + size]
                        self.position += size
                        return result

                def decode(self, encoding="utf-8"):
                    return self.data.decode(encoding)

            return {"Body": BytesIOWrapper(content), "ContentLength": len(content)}
        except Exception as e:
            raise Exception(f"Error reading file {key}: {str(e)}")

    def list_objects(self, prefix: str = "") -> List[Dict[str, Any]]:
        """
        プレフィックスに一致するオブジェクトの一覧を取得

        Parameters
        ----------
        prefix : str, optional
            プレフィックス, by default ""

        Returns
        -------
        List[Dict[str, Any]]
            オブジェクトの一覧
        """
        prefix_path = self.base_dir / prefix
        prefix_dir = prefix_path if prefix_path.is_dir() else prefix_path.parent

        if not prefix_dir.exists():
            return []

        objects = []
        for root, _, files in os.walk(prefix_dir):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.base_dir)
                rel_path_str = str(rel_path).replace("\\", "/")

                if rel_path_str.startswith(prefix):
                    objects.append(
                        {
                            "Key": rel_path_str,
                            "Size": file_path.stat().st_size,
                            "LastModified": date.fromtimestamp(
                                file_path.stat().st_mtime
                            ),
                        }
                    )

        return objects

    def delete_object(self, key: str) -> None:
        """
        オブジェクトを削除

        Parameters
        ----------
        key : str
            削除するキー（パス）
        """
        file_path = self.base_dir / key
        if file_path.exists():
            os.remove(file_path)


local_storage = LocalStorage()
