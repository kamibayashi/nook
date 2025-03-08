"""
ローカルでLambda関数を実行するためのランナーモジュール
"""

import importlib
import os
import sys

from datetime import date
from typing import List, Dict, Any


def setup_environment() -> None:
    """
    環境変数を設定
    """
    # 環境変数にローカルストレージのパスを設定
    os.environ["LOCAL_STORAGE"] = "true"
    os.environ["BUCKET_NAME"] = "local-bucket"

    # データディレクトリを作成
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    print(f"データディレクトリを確認: {data_dir}")


def import_lambda_module(module_name: str) -> Any:
    """
    Lambda関数のモジュールをインポート

    Parameters
    ----------
    module_name : str
        モジュール名

    Returns
    -------
    Any
        インポートしたモジュール
    """
    # Lambda関数のディレクトリをパスに追加
    lambda_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lambda"
    )
    module_dir = os.path.join(lambda_dir, module_name)

    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    # 共通モジュールのディレクトリもパスに追加
    common_dir = os.path.join(lambda_dir, "common")
    if common_dir not in sys.path:
        sys.path.insert(0, common_dir)

    common_python_dir = os.path.join(common_dir, "python")
    if common_python_dir not in sys.path:
        sys.path.insert(0, common_python_dir)

    # モジュールをインポート
    return importlib.import_module(module_name)


def create_lambda_event(module_name: str, target_date: date) -> Dict[str, Any]:
    """
    Lambda関数のイベントを作成

    Parameters
    ----------
    module_name : str
        モジュール名
    target_date : date
        対象日付

    Returns
    -------
    Dict[str, Any]
        Lambda関数のイベント
    """
    # EventBridgeからのイベントをシミュレート
    return {
        "source": "aws.events",
        "time": target_date.isoformat() + "T00:00:00Z",
        "requestContext": {"http": {"method": "GET"}},
        "queryStringParameters": {"date": target_date.isoformat()},
    }


def run_collector(modules: List[str], target_date: date) -> None:
    """
    情報収集と要約を実行

    Parameters
    ----------
    modules : List[str]
        実行するモジュールのリスト
    target_date : date
        収集する日付
    """
    # 環境設定
    setup_environment()

    # 各モジュールを実行
    for module_name in modules:
        print(f"実行中: {module_name}...")

        # Lambda関数のモジュールをインポート
        try:
            lambda_module = import_lambda_module(module_name)
        except ImportError as e:
            print(f"エラー: モジュール {module_name} のインポートに失敗しました: {e}")
            continue

        # Lambda関数のイベントを作成
        event = create_lambda_event(module_name, target_date)
        print(event)

        # Lambda関数を実行
        try:
            result = lambda_module.lambda_handler(event, None)
            print(
                f"完了: {module_name} - "
                f"ステータスコード: {result.get('statusCode', 'unknown')}"
            )
        except Exception as e:
            print(
                f"エラー: モジュール {module_name} の実行中にエラーが発生しました: {e}"
            )
            import traceback

            traceback.print_exc()
