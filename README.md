# NewsBot 📰
**キーワードフィルタリングによる複数のRSSフィードを監視するDiscordボット**

NewsBotは、設定された複数のReally Simple Syndication (RSS)フィードを監視する自動化されたDiscordボットです。各フィードの記事のタイトルまたは概要に定義済みのキーワードが含まれているかを確認し、重複投稿を防ぎながら、関連ニュースのバッチを指定されたDiscordチャンネルに送信します。

## ✨ 機能
*   **複数フィード対応:** さまざまなソースからの複数のRSSフィードを解析します。
*   **キーワードフィルタリング:** 定義された特定のキーワードを含む記事のみを報告します（大文字・小文字を区別しません）。
*   **重複排除 (Deduplication):** ローカルのSQLiteデータベース (`topics_watcher.db`) を使用して、投稿済みの記事URLを追跡し、重複投稿を防ぎます。
*   **Discord連携:** 最大10件までの構造化されたDiscord埋め込み（Embeds）にニュース更新を送信します。
*   **システムトレイ監視:** 永続的なシステムトレイアイコンを提供し、ステータス確認や設定更新が容易に行えます。

## 🚀 セットアップ方法

### 前提条件
Pythonがインストールされている必要があります（Python 3.8以上を推奨）。

### インストール
ルートディレクトリ (`D:\Workspaces\DiscordBot\NewsBot`) に移動し、必要なすべての依存関係をインストールします。

```bash
pip install -r requirements.txt # requirementsファイルがある場合。なければ手動で以下を実行してください:
pip install discord python-dotenv pystray beautifulsoup4 feedparser
```

### 設定 (Configuration)
このボットは、主に3つの設定ソースに依存しています：

1.  **`.env`**: 機密情報（DiscordトークンやチャンネルID）を保存します。
    *   `DISCORD_TOKEN`: あなたのDiscord Botトークン。
    *   `DISCORD_CHANNEL_ID`: ニュースアラートが送信されるべきチャンネルのID。

2.  **`config/config.json`**: チェック頻度やソースリストのパスを含む、グローバルなボット設定。
3.  **`.config/config.json` (フィードデータ)**: 監視するフィード (`favorites`) と検索に使用するキーワード (`keywords`) を定義した運用データです。

**`.config/config.json` の設定例:**
```json
{
    "keywords": {
        "Technology": { "word": "technology", "source": "keyword" },
        "Crypto": { "word": "crypto", "source": "keyword" }
    },
    "favorites": [
        { "type": "rss", "name": "テックニュースフィード1", "url": "http://example.com/feed1.xml" },
        // 他のフィードを追加してください
    ]
}
```

## 🛠️ プロジェクト構造の概要 (Project Structure Overview)
コアロジックは、関心の分離を目的として複数のモジュールに分割されています。

*   `app.py`: メインのエントリーポイントです。ボットを初期化し、バックグラウンドスレッドでDiscordイベントループを開始し、システムトレイメニューを設定します。
*   `src/config.py`: 主要な `config.json` からグローバル設定を読み込む役割を担います。
*   `src/feed_collector.py`: 記事の取得を管理します。RSSフィードを解析（`feedparser`）、キーワードに基づいてエントリをフィルタリングし、HTMLタグをクリーンアップした後、重複チェックのために `topics_watcher` を呼び出し、新しいトピックのリストを生成します。
*   `src/discord_sender.py`: Discord APIとの通信を担当します。発見されたトピックオブジェクトのバッチを受け取り、構造化された埋め込み形式で送信します。
*   `src/topics_watcher.py`: `topics_watcher.db` (SQLite) とやり取りすることで永続性を管理し、時間経過と共に固有の記事のみが処理されることを保証します。

## ⚙️ 仕組みの流れ (How It Works / フロー)

1.  **起動:** ユーザーが `app.py` を実行します。
2.  **初期化:** ボットは設定を読み込み、既知のURLを追跡するためのSQLiteデータベースを初期化します。
3.  **Discordスレッド:** バックグラウンドスレッドがDiscordクライアント接続を開始し、準備完了を待ちます。
4.  **システムトレイ:** システムトレイメニューが表示され、メインプロセスを実行せずにステータスの確認や設定更新が可能になります。
5.  **スケジュールタスク (ループ):** `check_interval_minutes` に基づいて定期的なループがトリガーされます：
    *   `feed_collector` が設定されたRSSフィードを反復処理します。
    *   各フィードエントリについて、タイトル/概要に定義されたキーワードが含まれているかを確認します。
    *   次にローカルデータベース（`topics_watcher`）に問い合わせを行い、記事URLが既に投稿されていないか確認します。
    *   もし新しく関連性の高い記事であれば：
        1.  ボットはそのURLをデータベースで送信済みとしてマークします。
        2.  構造化されたトピックオブジェクトを作成します。
    *   収集されたユニークな全てのトピックが `discord_sender` に渡されます。
6.  **レポート:** `discord_sender` は、トピックのバッチをまとめ、美しいDiscord埋め込み形式として投稿します。

## 🛑 ボットの実行方法

メインアプリケーションファイルを実行してください。

```bash
python app.py
```

ボットはフォアグラウンドで実行され、コンソールにログイン完了およびその後のメッセージ送信の確認メッセージが表示されるはずです。システムトレイアイコンも表示され、アクティブな状態であることを示します。