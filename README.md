# プロコン発表用
> ### **webシステム(環境, 使用言語, フレームワーク, パッケージ, ライブラリ, DB, ファイル 等...)**
* AWS
    * Amazon Simple Email Service
* Docker
* nginx
* Python
    * gunicorn
    * Django
        * django-allauth
        * django-bootstrap-datepicker-plus
        * django-ses
        * boto
    * psycopg2-binary
    * openpyxl
    * pillow
    * Pandas
    * NumPy
    * Scipy
    * sklearn
    * matplotlib
    * TensorFlow
    * Keras
* JavaScript
    * Chart.js
    * jQuery
        * FullCalendar
* Ajax
* CSS
* Bootstrap
* PostgreSQL
* WEB API
    * Google OAuth 
    * Google map API
        * Geocoding API
        * Maps JavaScript API
    * Geolocation API
* json, csv, xlsx


> ### **webシステム(全体像)**
<img width="2371" alt="WEBシステム" src="https://user-images.githubusercontent.com/71476154/107870940-7cc5ce80-6ee0-11eb-8828-5a92788b6264.png">


> ### **webシステム(概要)**

* ユーザ
	* 会員登録
		* バリデーション
		* 免許判定AI
			* 画像処理
				* TensorFlow(h5)
		* 二段階認証
			* ソーシャルアカウントログイン
				* Google OAuth 
			* Allauth(Django)
	* カーシェア予約方法
		* 地図から
			* 自宅
				* Google map API
			* 現在地
				* Google map API
				* Wi-Fiから位置情報取得
					* Geolocation API
		* 車から
			* 非同期検索(JavaScript)
			* 条件検索(Django)
		* お気に入りから
			* 登録処理
				* getでredirect先の分岐
		* 過去の履歴から
	* カーシェア予約処理
		* 入力
			* 入力フォーム
				* DatePicker
					* (Django, Bootstrap)
			* バリデーション
		* 排他制御
			* オーナー貸し出し制限
			* 重複予約回避
		* FullCalendar
		* プラン別料金計算(jQuery)
		* 予約完了メール
			* Django-ses
			* AWS SES
		* QRコード生成
			* Google Chart API
		* 返却処理
			* メール送信
				* Django-ses
				* AWS SES
			* おすすめAI起動
				* クラスタ分析
					* K-means
					* Pandas / NumPy (Python)
				* Jsonデータ生成
	* 駐車場予約
		* バリデーション
		* メール送信
			* Django-ses
			* AWS SES
	* マイページ
		* ユーザ情報確認
		* 予約一覧
			* 非同期切り替え
		* 利用明細
			* ページネーション
			* 非同期切り替え
		* カレンダー
			* FullCalendar
* モバイルアプリ
	* 自作 WEB API
		* GETで条件検索(Django)
		* HttpResponse Json書出し
* タイマー処理
	* 月に一度
		* ユーザの料金チャージ
		* ユーザ変更処理
			* プラン変更処理
			* クレカ期限チェック
		* 価格予測AI起動
			* Pandas / NumPy (Python)
			* Jsonデータ生成
	* 週に一度
		* 配車予測AI起動
			* ユーザ利用地域収集
			* Pandas / NumPy (Python)
			* Jsonデータ生成
* 管理者
	* 車両登録
		* バリデーション
	* 駐車場登録
		* 座標取得
			* Ajax通信
		* バリデーション
		* 駐車場タイプ入力制御(JavaScript)
		* エリア自動分類登録(Django)
	* 配車管理AI
		* 過不足判定AI
		* UI
			* Google map API
		* 配車管理
			* 車両の設定と解除
	* アンケート結果
		* Google Chart API
	* DBデータ自動入力
		* import(csv, xlsx, json)
* 中古車購入
	* おすすめAI
		* Jsonデータ参照
	* 検索
		* ページネーション
		* メーカー検索
		* 詳細画面
			* グラフ描画
				* Chart.js
			* スクレイピング
				* DB自動格納
	* 価格推移AI
		* Jsonデータ参照
		* グラフ描画
			* Chart.js
* オーナ
	* オーナ登録
		* バリデーション
		* 銀行支店コード判定
	* 車両登録
		* バリデーション
	* 駐車場登録
		* 座標取得
			* Ajax通信
		* バリデーション
		* 駐車場タイプ入力制御(JavaScript)
		* エリア自動登録(Django)
	* オーナー貸し出し制限

# ---------------- 発表用 ----------------

# django-sample
**#編集する箇所**
1. nginx/nginx.confの1.静的ファイルの要求をstaticfilesにルーティング
2. docker-composeのappとnginxの volumes: -static_volume/~/app/◯◯←〇〇を変更

# 開発開始 コマンドまとめ
##Docker
```
$docker-compose up --build -d(1回のみ)
$docker-compose exec app bash
$docker-compose stop
$docker-compose start(2回目以降)
```
##pipenv
```
$pipenv install --system
```
##Django
```
$python manage.py migrate
$python manage.py collectstatic(やらないとcssや画像が反映されない)
$gunicorn --bind 0.0.0.0:8000 config.wsgi:application(runserverと同じ感じ)(http://0.0.0.0:1337/~でサイト閲覧可能)
control + c
```
# 修正箇所


**＃1**

* ~~トップページの画像が大きすぎる。画面の半分か1/3くらいでもよいのでは？~~
* ~~メンバー登録の入力チェックは大丈夫？全角入力とか「－」入力した・しないとか。~~
* メンバー登録でGoogleの登録情報は持ってこれない？
* ~~メニューが分かりにくい~~
    * ~~例えば、「中古車」ではなく「中古車購入」とか。~~
    * ~~オーナーのサブメニューの文字列も長い。~~

    
**＃2**

* ~~予約済情報をトップページの見やすいところに欲しい~~
* ~~駐車場の細かな条件（立体・平地、砂利・コンクリ・砂）あった方がいい。~~
* ~~予約時間が分単位でできるのであれば微妙かも。料金計算とか。~~
* ~~車検索結果の一覧にある”ID”は必要？ 利用者はなんのIDか分からない。~~
* ~~確定ページで、”完了メールを送ったからみてねー”的なの必要。~~
* ~~「確定」押した後にいきなりトップに行くのはびっくりする。予約確定ページがあった方がよい。~~
* ~~サブスクとか定期予約とかできたら便利だね。~~
* ~~予約するときに料金が分からないのは不安。~~
* ~~「スタットレス」じゃなくて「スタッドレス」、ね。~~


**＃3**

* ~~料金設定はどうやる？~~
    * ~~登録の時にするとは思うが。~~
    * ~~初めて登録する人は相場が分かりにくいはず。~~
    * ~~途中で変更するのはクレームのもとになるしね。~~
* 貸出しは可能日か不可能日かを選べるようにしたい
* ピンだけで場所確定は心配。 ピン立てたあとに修正したい。
* ~~車両→駐車場の流れに遊びがない。~~
    * ~~駐車場の登録をしない人とか、後でしたい人とかも出てくるはず。~~
    * ~~その選択肢が見えたほうがよい。~~
* ~~車登録で「走行距離」があってもよい。~~
    * あとは傷とかは？
    * ~~あと、オプションあっても良い。~~
    * ~~例えば、ベビーシート、タイヤ、自動運転、ETC、カーナビとか。~~


**＃4**

* ~~アンケートの取り方が微妙。~~
    * ~~カーシェア後のアンケートなら、車やサービスに対してでは？~~
    * ~~中古車買わせたい感が強すぎるのかな。~~
* 予約とか登録するときの「利用規約」てきなの必要な。
    * 事故ったときの責任とか、遅延料とか。んで、了承させておく必要あるね。
* ~~価格予想の今後に期待・・・！！~~


**＃5**

* ~~返却時のアクションが必要では？~~
    * ~~予約時のメールとかサイトに「返却処理ページ」のリンクとかつけて、そこで問題なかったか（事故ったりしてないかとか、ガソリン残量とか）を入力させる。~~
    * ~~んで、アンケートも簡単な仕様になってるから、そこで必須入力にすれば入力率100％になるし。~~
* ~~予約の排他制御は・・・ まぁ、いいか・・・~~
* ~~スマホのインタフェースはチェックしてる？ 若者ターゲットなのでそっちも忘れずに！~~


**＃6**

* ~~ユーザ登録時に免許証の写真データ提出を必須にしては？~~
    * ~~んで、入力情報とマッチングさせる。~~
    * ~~未成年とか無免許者がカーシェアできてしまう作りは問題だね。~~
* ~~車登録するときに写真もアップできた方が良いのでは？~~



# :christmas_tree:冬休み期間のお願い:christmas_tree:

- ***作業前に "必ず" どのファイルを編集するか伝えること！***

- ***pullした時、以下のように「＋」や「ー」が表示されているか確認すること！！！！***
    ```
    templates/carsharing_req/base.html  | 97 ++++++++++++++++++++--------
    ```

- ***不安ならもう一度pullしてみて以下のような表示ならOK！***
    ```
    From https://github.com/kawanishi291/proconEF
    * branch            django     -> FETCH_HEAD
    Already up to date.
    ```

- ***Teamsで連絡した際、既読後スタンプで反応すること！！***

- ***分からない事があるなら通話orチャットで聞くこと！***
    - *月・火・木・金の 16:00~22:00 は連絡が取れませんチャットでお願いします。*
    - *皆さんも連絡されたくない日にち時間帯は予め教えてください* :pray:

- ***作成時、何をするためのものかコメントを残すこと！***
    - *自作の変数にも日本語の説明や(代入される想定の)型などを書いていただくと丁寧だと思います。*
    - *cssのclass, idも同様に何処に反映するか軽く日本語でメモして置くと、作業がしやすいです。*

- ***commitする際、日にちに加えてやった内容も記載すること！！***
    - *pullreq後のチェックがし易く、皆さん自身が見返す時にかなり便利です。*

- ***自分が書いてないコードを止むを得ず消す場合は必ずコメントアウトにすること！！！***

- ***必要のなくなったコメントアウトは削除してからpushすること***

- ***バグ・エラーがないか確認する為、システムをたくさん動かすこと***
    - *見つかったら自分で直す前にすぐ報告！！！*

- ***APIやパッケージをInstallする前に相談すること！！！***

###### ＊基本的にリモートで会議などするつもりはありません。
###### 　全員の面倒を見ることができる環境でない為、自分から積極的に行動してください。:shit:
###### ＊人生最後の長期休みです。ちゃんと遊んでください。ゆっくり休んで、思いっきり楽しんでください！！:santa:
###### （やるべき事をちゃんとやっていれば大丈夫:+1:）

# 今後の予定
    
> ### **既存の機能**

**○アンケートの作成**

* ~~モデルとフォームを作成~~
* ~~3~4項目を毎回ランダムに抽出し回答させる~~
* ~~未回答のカラム→random関数~~

**○オーナーの予約可能時間設定**

* ~~既存の予約モデルを利用し貸し出し不可能時間を登録~~
* ~~カレンダーを作成し確認画面を作成~~

**○カレンダー**

* ~~FullCalendarを利用し、予約や貸し出し日時を全て一括確認する~~

**○免許証、クレカ(ユーザ)・銀行口座(オーナ)登録**

* ~~免許は画像アップロード機能を使用~~
* ~~クレカと口座は情報をハッシュ化し、下3桁のみ表示~~

**○管理者の駐車場仕様変更**

* ~~ピンを立てるのは駐車場でなくステーション~~
* ~~収容台数。管理者チェックボックス。制限台数フラグを追加~~
* ~~車を追加する際にステーションと結びつける~~
* ~~つまり駐車場を検索する際はステーション毎に予約する仕様~~
* ~~一つの駐車場IDに複数台追加可能~~
* ~~予約の際は駐車場を選んだ後、車両を選択~~

**○配車予測機能**

* 予測データから配車場所を追加する
* あらかじめ中心地となる座標を指定し格納
* 最も近い値の座標の地域IDをそれぞれ設定
* ステーションIDはより細かくする！
* 目安の数値を決めてそれ以下なら同じステーションIDを割り振り
* ステーションID毎に計算させる！

**○予約の重複を回避**

* ~~予約テーブルから検索~~

**○予約方法**

* ~~地図から検索~~
* ~~車から検索~~
* ~~履歴から検索~~


> ### **新機能最低３つ**

* ~~メール送信~~
* 電気自動車
* 特殊車両


> ### **デザイン**

* リンク先ルーティング設定
* メディアクエリに対応させるcss作成
* 動画や画像で使い方を説明
* 利用時の必要事項ページ作成


# info

> **日付入力をカレンダー方式にする方法**

django-bootstrap-datepicker-plusをインストールし、フォームクラス上のwidgetにライブラリのクラスを指定
```
pip install django-bootstrap-datepicker-plus
```
参考サイト:

[[Django] 日付入力欄をカレンダー形式にする (bootstrap-datetimepicker)](https://qiita.com/okoppe8/items/999b8e3c86708fbb3926)


> **DjangoにおけるDB操作 クエリメソッド（QueryAPI）**

参考サイト:

[Django 逆引きチートシート（QuerySet編）](https://qiita.com/uenosy/items/54136aff0f6373957d22#%E6%A4%9C%E7%B4%A2%E7%B3%BB)

[Django データベース操作 についてのまとめ](https://qiita.com/okoppe8/items/66a8747cf179a538355b)

[Django フィールドのアップデートのやりかた](http://wpress.biz/blog/2017/02/25/django%E3%83%95%E3%82%A3%E3%83%BC%E3%83%AB%E3%83%89%E3%81%AE%E3%82%A2%E3%83%83%E3%83%97%E3%83%87%E3%83%BC%E3%83%88%E3%81%AE%E3%82%84%E3%82%8A%E3%81%8B%E3%81%9F/)

[Django QuerySetのfilterメソッドの使い方まとめ](https://codelab.website/django-queryset-filter/#i-13)

> **DjangoにおけるSESSION利用法**

参考サイト:

[【Django】Sessionの使い方（基本編）](https://idealive.jp/blog/2018/11/21/%E3%80%90django%E3%80%91session%E3%81%AE%E4%BD%BF%E3%81%84%E6%96%B9%EF%BC%88%E5%9F%BA%E6%9C%AC%E7%B7%A8%EF%BC%89/)

> **Bootstrapを利用し簡単に形を整える**

参考サイト:

[【Bootstrap】の基本「マージン」と「パディング」](https://design-studio-f.com/blog/bootstrap-utilities-spacing/)

[スクロールに応じてトリガーするJavaScriptのライブラリ「ScrollTrigger」](https://www.willstyle.co.jp/blog/2869/)

# proconEF($の付いているものはターミナルかコマンドプロンプトで実行)
* Gitコマンド&流れ(エラーや質問は森正or斉藤へ)
## 11/4日にやること(1回のみ！！！)
```
1. 翔ちゃんのGithub(proconEF)をForkする
2. $cd Desktop #自分のPCのデスクトップに移動 
3. $git clone 自分のGithubURL(proconEF) #URL先のフォルダを自分のPC上にコピー
4. $cd proconEF #proconEFに移動
5. $git remote add remote 翔ちゃんのGithubURL(proconEF) #URL先のフォルダをremoteという名前で追加
6. $git update-index --skip-worktree Pipfile Pipfile.lock config/settings.py
7. VSCodeの左下のmainを押してorigin/djangoをクリック(branchを変更)
8. Djangoでの開発の流れの 11/4日にやること(1回のみ！！！)を実行
```

## 毎回開発の前にやること(proconEFフォルダ内で)
```
1. VSCodeの左下のmainを押してdjangoをクリック(branchを変更)
2. $git pull remote django #前日の変更をローカルに適用
3. 仮想環境の設定を実行
```

## 毎回開発後にやること(proconEFフォルダ内で)
```
1. $git add .
2. $git commit -m "コメント入力"
3. $git push origin django #１,2,3,を実行することで自分のGithubのproconEFのdjangoブランチに変更が送られる
4. Githubのcode下にあるmain▼をdjangoに変更
5. Githubからpull requestsをクリック→翔ちゃんのproconEF djangoに自分のproconEF djangoからcreate pull requestを作成
```

# Djangoでの開発の流れ 
## 11/4日にやること(1回のみ！！！)
```
1. $cd Desktop #Desktopに移動
2. $pip install pipenv
3. 仮想環境の設定を実行
```

## 仮想環境の設定(開発の時毎回やる)
```
$cd Desktop
$cd proconEF
$pipenv install #仮想環境の作成
$pipenv shell #仮想環境に入る(VSCodeのshellが$pipenv or Python~に変わっているか確認)
```

## Djangoコマンド
```
python manage.py makemigrations #データベースにテーブル作成
python manage.py migrate #データベースへ反映
python manage.py createsuperuser #管理者アカウントの作成
python manage.py runserver #サーバー起動
```

## DB削除

1. 全てのアプリケーションの*migrations*フォルダ内の*0001_initial.py*を削除
2. 以下のコマンドを実行
```
$ rm db.sqlite3 #データベースを削除
```
3. 上の4つの**Djangoコマンド**を実行
