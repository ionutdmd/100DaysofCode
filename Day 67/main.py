import datetime

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post", )


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    blog_post = db.session.get(BlogPost, post_id)
    if blog_post:
        return render_template("post.html", post=blog_post)
    else:
        return "Sorry! A post with this id does not exist on the server"


@app.route("/new_post", methods=["GET", "POST"])
def add_new_post():
    new_post_form = CreatePostForm()
    if new_post_form.validate_on_submit():
        new_post = BlogPost(
            title=new_post_form.title.data,
            subtitle=new_post_form.subtitle.data,
            date=datetime.datetime.now().strftime("%B %d, %Y"),
            body=new_post_form.body.data,
            author=new_post_form.author.data,
            img_url=new_post_form.img_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=new_post_form, title="New Post")


@app.route("/edit-post/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post_to_update = db.session.get(BlogPost, post_id)
    edit_post_form = CreatePostForm(
        title=post_to_update.title,
        subtitle=post_to_update.subtitle,
        author=post_to_update.author,
        img_url=post_to_update.img_url,
        body=post_to_update.body
    )
    if edit_post_form.validate_on_submit():
        edited_post = BlogPost(
            title=edit_post_form.title.data,
            subtitle=edit_post_form.subtitle.data,
            body=edit_post_form.body.data,
            author=edit_post_form.author.data,
            img_url=edit_post_form.img_url.data
        )
        post_to_update.title = edited_post.title
        post_to_update.subtitle = edited_post.subtitle
        post_to_update.author = edited_post.author
        post_to_update.img_url = edited_post.img_url
        post_to_update.body = edited_post.body
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_to_update.id))
    return render_template("make-post.html", form=edit_post_form, title="Edit Post")


@app.route("/delete/<post_id>")
def delete_post(post_id):
    post_to_delete = db.session.get(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
