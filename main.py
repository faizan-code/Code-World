
from flask import Flask, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json
import os
from werkzeug.utils import secure_filename
import math
# tutorial for sqlalchemy  - https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/



with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True



app = Flask(__name__)
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = params['']

app.secret_key = 'super-secret-key'
# belw i am doing mail authotentication using flask_mail.
app.config['UPLOAD_FOLDER'] = params['uplaod_location']
app.config.update(

    # all configuration can be get from flask_mail documentation.
    # link - https://pythonhosted.org/Flask-Mail/
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    # 465 is the default parameter for gmail.,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)

mail = Mail(app)






# SEE BELOW CODE THIS WILL BE SAME TO CONNECT SQL_ALCHEMY

#see json file for it.

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']


db = SQLAlchemy(app)

# I got this code and above 2 line code from link below
# link - https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
# simply search flask_sqlalchemy pocoo  documentation.
# similarly we can search flask and particular model documentaion to do task.


class Contacts(db.Model):
    """
        sno,name,email,phone_num,msg,date

    """
    # note unique = False means unique value is not necessary
    # nullable = True means null value is allowed. and by default its value is True.

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone_num = db.Column(db.String(150), nullable=False)
    msg = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=False)



class Posts(db.Model):
    """
        sno,name,email,phone_num,msg,date
    """
    # note unique = False means unique value is not necessary
    # nullable = True means null value is allowed. and by default its value is True.

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    # Note Posts.query() here Post is the class name see above
    posts = Posts.query.filter_by().all()
   # [0:params['no_of_posts']]

    # last page we need to find it by total post/no_of_post
    # no_of_post means how manhy post can be there in a single page

    last = int(math.ceil(len(posts)/int(params['no_of_posts'])))

    #[0: params['no_of_posts']]

    #posts = posts[]

    page = request.args.get('page')

    if(not str(page).isnumeric()):
        page = 1
    page = int(page)


    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if (page == 1):
        prev = "#"
        next = "/?page="+str(page+1)
    elif(page==last):
        next = "#"
        prev = "/?page=" + str(page - 1)
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)






    return  render_template('index.html', params=params, posts=posts, prev=prev, next=next)

#@app.route("/post/", methods=['GET'])
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route("/about")
def about():
    return render_template('about.html', params = params)



@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    # If user already logged in

    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts = posts)

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts = posts)

    return render_template('login.html', params=params)




            #REDIRECT TO ADMIN PANEL



@app.route("/edit/<string:sno>", methods = ['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()


            # if sno = 0 then it means we are adding a new post
            if sno == '0':
                post = Posts(title = box_title, slug = slug, content = content,tagline = tline,img_file = img_file, date = date)
                db.session.add(post)
                db.session.commit()


            # if sno != 0  then we are editing our previous post
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()

                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params = params, post=post)



@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    # We want to change file when a user is logged in in our server.
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded Successfully"



@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')



@app.route("/delete/<string:sno>", methods = ['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')













@app.route("/contact", methods = ['GET', 'POST'])

# SEE LINE 30 OF Contact.html there we can see we did
# action = /contact so when we will submit in contact then it will
# submit out input to /contact end point.

# we also did method = post so that that message can be posted.

# use of get and post

def contacts():
    if (request.method=='POST'):
        """ Add entry to the database"""

        # See below form is used.


        # name = request.form.get('name')
        # above 'name' should be equal to the name  of the tag in html see
        # html code of contact there i have define name of email as 'email'
        # rember that.

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        """
                sno,name,email,phone_num,msg,date

        """

        # see below code belong to lect_8 see below left hand side me
        # sql table ka col ka nam rhe ga or right mee jo var upr define kiye hai.

        entry = Contacts(name=name, phone_num=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        # below line we write 'New message from' + name this + name will take the name
        # of the contact prson from the data base and put in the message we get
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + phone
                          )
    return render_template('contact.html', params=params)

app.run(debug=True)


#This is my flask application where you can connect with different coders all around the globe and shares your knowledge and help other.