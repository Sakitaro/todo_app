from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for    #requestはGETやPOSTのようにリクエスト方法に応じて実装内容を変更するために必要　
from flask_sqlalchemy import SQLAlchemy         # redirectはPOSTで受け取った内容をデータベースに反映した後に、もう一度トップページへアクセスするため
from datetime import datetime, date


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


#データベースの項目定義
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

def create_default_tasks():
    # デフォルトのタスクをデータベースに追加する
    default_tasks = [
        {'title': 'Task 1', 'detail': 'Detail for Task 1', 'due': datetime.now()},
        {'title': 'Task 2', 'detail': 'Detail for Task 2', 'due': datetime.now()},
        {'title': 'Task 3', 'detail': 'Detail for Task 3', 'due': datetime.now()}
    ]
    for task in default_tasks:
        new_post = Post(title=task['title'], detail=task['detail'], due=task['due'])
        db.session.add(new_post)
    db.session.commit()


#GET: 保存されているタスクを表示  POST: データベースにタスクを保存
@app.route('/', methods=['GET', 'POST']) 
def index():
    # データベースから全ての投稿を取り出し、トップページに渡す
    if request.method == 'GET':
        posts = Post.query.order_by(Post.due).all()
        return render_template('index.html', posts=posts, today=date.today())

    else:
        # 1,POSTされた内容を受け取る
        # 2,Postクラスに受け取った内容を渡す
        # 3,データベースに投稿を保存する
        title = request.form.get('title') 
        detail = request.form.get('detail')
        due = request.form.get('due')

        due = datetime.strptime(due, '%Y-%m-%d') #文字列→日付型　データベースの定義で日付型を指定していたけど、フォームから受け取る値が文字列だから
        new_post = Post(title=title, detail=detail, due=due)

        db.session.add(new_post) #内容追加
        db.session.commit() # 実際に反映
        return redirect('/')


@app.route('/create')
def create():
    return render_template('create.html')


@app.route('/detail/<int:id>') # どの投稿の詳細ページを開くのか指定
def read(id):
    post = Post.query.get(id)  # 該当するidの投稿内容を取得

    return render_template('detail.html', post=post)


@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')

        db.session.commit()
        return redirect('/')

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
     
