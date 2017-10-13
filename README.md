# VCSearch

### 説明

Google Play で配布されているアプリの過去全ての version code を収集するスクリプト．


### 依存

[Protocol Buffer python runtime](https://github.com/google/protobuf/tree/master/python) のインストールが別途必要です．
(もしかしたら [Protocol Buffer compiler](https://github.com/google/protobuf) も必要かもしれません)
これらの依存パッケージは `pip install -r requirements.txt` で導入できます．


### 使い方

`python vc_search.py`
`vc` 以下に `パッケージ名.json` というファイルが生成され，アプリごとの version code が書き込まれます．


### 設定
config.py で Android デバイスID， Google アドレス，そのパスワードを設定する必要があります．
`PKG_FILEPATH` で指定されたファイル内に version code を収集したいパッケージ名をjsonの配列形式で保存してください．


### 注意

短期間に複数回このスクリプトを実行するとアカウントを凍結されるかもしれません．


### ライセンス

このツールの公開・利用・頒布に関する規定は BSD Lisence に従います．
