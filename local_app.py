import argparse
from datetime import date
from dotenv import load_dotenv

# ローカル実行用のモジュール
from nook.local.runner import run_collector
from nook.local.server import start_server

load_dotenv()


def main():
    """
    ローカル環境でNookを実行するためのエントリーポイント

    コマンドライン引数:
    - collect: 情報収集と要約を実行
    - serve: Webサーバーを起動
    """
    parser = argparse.ArgumentParser(description="Nook Local Runner")
    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # collect コマンド
    collect_parser = subparsers.add_parser("collect", help="情報収集と要約を実行")
    collect_parser.add_argument(
        "--date", type=str, help="収集する日付 (YYYY-MM-DD形式、デフォルトは今日)"
    )
    collect_parser.add_argument(
        "--modules",
        type=str,
        nargs="+",
        choices=[
            "reddit_explorer",
            "hacker_news",
            "github_trending",
            "tech_feed",
            "paper_summarizer",
            "all",
        ],
        default=["all"],
        help="実行するモジュール (デフォルトは全て)",
    )

    # serve コマンド
    serve_parser = subparsers.add_parser("serve", help="Webサーバーを起動")
    serve_parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="ホスト (デフォルト: 127.0.0.1)"
    )
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="ポート (デフォルト: 8000)"
    )

    args = parser.parse_args()

    if args.command == "collect":
        target_date = date.today()
        if args.date:
            try:
                target_date = date.fromisoformat(args.date)
            except ValueError:
                print(
                    "エラー: 日付の形式が無効です。YYYY-MM-DD形式で指定してください。"
                )
                return

        modules = args.modules
        if "all" in modules:
            modules = [
                "reddit_explorer",
                "hacker_news",
                "github_trending",
                "tech_feed",
                "paper_summarizer",
            ]

        run_collector(modules, target_date)

    elif args.command == "serve":
        start_server(host=args.host, port=args.port)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
