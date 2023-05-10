from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_mail import Mail,Message
import pymysql
import random
import smtplib

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import os
import requests
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='aikumask',
                             database='learnify',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pothamsettychethan@gmail.com'
app.config['MAIL_PASSWORD'] = 'azfzbfnbwvdfehzo'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
#proxy_host='10.10.78.22'
#proxy_port='3128'
#proxy_username='cs1210561'
#proxy_password='aikumask'
#smtp_server=smtplib.SMTP(proxy_host,proxy_port)
#smtp_server.starttls()
#smtp_server.login(proxy_username,proxy_password)
mail = Mail(app)
mail.init_app(app)
app.secret_key = '^$*Hdd68*f'
app.config["F"]="/home/baadalvm/Learn/static/imgs"

@app.route("/forgotPassword",methods=["POST"])
def sendMail():
    global OTP
    username = request.form["username"]
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user WHERE username = %s",(username,))
        user = cursor.fetchone()
        connection.commit()
    s = "Your OTP for verification is: "
    c = ""
    for i in range(4):
        a = random.randint(0,9)
        s += str(a)
        c += str(a)
    session["otp"] = c
    msg = Message(body=s,sender="pothamsettychethan@gmail.com",recipients=[user["email"]])
    mail.send(msg)
    return render_template("otp.html",username=username)

@app.route("/OTP",methods=["POST"])
def verifyotp():
    o1 = request.form["o1"]
    o2 = request.form["o2"]
    o3 = request.form["o3"]
    o4 = request.form["o4"]
    otp = o1+o2+o3+o4
    usernamed = request.form["username"]
    if otp == session["otp"]:
        session.pop("otp",None)
        return render_template("password.html",username=usernamed)
    else:
        session.pop("otp",None)
        flash("Incorrect OTP")
        return redirect("/login")
@app.route("/newpassword",methods=["POST"])
def updatePassword():
    new_password = request.form["new_password"]
    username = request.form["username"]
    with connection.cursor() as cursor:
        cursor.execute("UPDATE user SET password = %s WHERE username = %s",(generate_password_hash(new_password),username))
        connection.commit()
    return redirect("/login")

@app.route("/profile")
def profile():
    if 'username' in session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE id = %s",(session["id"],))
            user = cursor.fetchone()
            connection.commit()
        return render_template("profile.html",user =user)
    else:
        flash("login required")
        return redirect("/login")

@app.route("/viewprofile/<int:id>")
def viewprofile(id):
    if 'username' in session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE id = %s",(id,))
            user = cursor.fetchone()
            connection.commit()
        return render_template("viewprofile.html",user =user)
    else:
        flash("login required")
        return redirect("/login")

@app.route("/editprofile",methods=["POST","GET"])
def editprofile():
    if 'username' in session:
        if request.method == "POST":
            firstname = request.form["firstname"]
            lastname = request.form["lastname"]
            email = request.form["email"]
            with connection.cursor() as cursor:
                sql = f"UPDATE user SET firstname=%s,lastname=%s,email=%s WHERE id=%s"
                cursor.execute(sql,(firstname,lastname,email,session["id"]))
                connection.commit()
            return redirect("/profile")
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE id = %s",(session["id"],))
                user = cursor.fetchone()
                connection.commit()
            return render_template("editprofile.html",user=user)
    else:
        flash("login required")
        return redirect("/login")
@app.route("/home")
def ind():
    if 'username' in session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM course ORDER BY rating DESC")
            courses = cursor.fetchall()
            courses1 = courses
            connection.commit()
        return render_template("Homepage.html",courses = courses[:20], courses1 = courses1[:20])
    else:
        flash("login required")
        return redirect("/login")

@app.route("/")

def index():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM course ORDER BY rating DESC")
        courses = cursor.fetchall()
        courses1 = courses
        connection.commit()
    return render_template("index.html",courses = courses[:20], courses1 = courses1[:20])
@app.route("/ins")
def fr():
    if 'username' in session:
        user_id = session["id"]
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM course WHERE user_id = %s",(user_id,))
            courses = cursor.fetchall()
            connection.commit()
        return render_template("instructorcourse.html",courses = courses)
    else:
        flash("login required")
        return redirect("/login")
@app.route("/become_instructor")
def ins():
    if 'username' in session:
        user_id = session["id"]
        with connection.cursor() as cursor:
            cursor.execute("UPDATE user SET isInstructor = %s WHERE id = %s",(True,user_id))
            cursor.execute("SELECT * FROM user WHERE id = %s",(user_id,))
            user = cursor.fetchone()
            connection.commit()
        return render_template("instructor.html",user=user)
    else:
        flash("login required")
        return redirect("/login")
@app.route("/course",methods = ["POST","GET"])
def addcourse():
    if 'username' in session:
        if request.method == "POST":
            courseName = request.form["courseName"]
            categoryName =request.form["categoryName"]
            user_id=session["id"]
            thumbnail = request.form["thumbnail"]
            description = request.form["description"]
            with connection.cursor() as cursor:
                sql = f"INSERT INTO course (name,category_name,user_id,thumbnail,description,rating,numofreviews) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (courseName, categoryName,user_id,thumbnail,description,0,0))
                cursor.execute("SELECT * FROM course WHERE id = %s",(cursor.lastrowid,))
                course = cursor.fetchone()
                cursor.execute("SELECT * FROM user WHERE id = %s",(user_id,))
                user = cursor.fetchone()
                connection.commit()
            return render_template("courseedit.html",course = course,user=user)
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE id = %s",(session['id'],))
                user = cursor.fetchone()
            return render_template("createcourse.html",u=session["id"],user=user)
    else:
        flash("login required")
        return redirect("/login")

@app.route("/video",methods = ["POST","GET"])
def addvideo():
    if 'username' in session:
        if request.method == "POST":
            name = request.form["name"]
            videoUrl = request.form["videoUrl"]
            description = request.form["description"]
            course_id = request.form["course_id"]
            with connection.cursor() as cursor:
                sql = f"INSERT INTO video (name,videoUrl,description,course_id) VALUES (%s,%s,%s,%s)"
                cursor.execute(sql,(name,videoUrl,description,course_id))
                cursor.execute("SELECT * FROM course WHERE id = %s",(course_id,))
                course = cursor.fetchone()
                cursor.execute("SELECT * FROM video WHERE course_id = %s",(course_id,))
                videos = cursor.fetchall()
                cursor.execute("SELECT * FROM pdf WHERE course_id = %s",(course_id,))
                pdfs = cursor.fetchall()
                cursor.execute("SELECT * FROM review WHERE course_id = %s",(course_id,))
                reviews = cursor.fetchall()
                cursor.execute("SELECT * FROM user WHERE id = %s",(session['id'],))
                user = cursor.fetchone()
                connection.commit()
            return render_template("courseedit.html",course = course,user=user,videos=videos,pdf=pdfs,reviews=reviews)
        else:
            return redirect("/home")
    else:
        flash("login required")
        return redirect("/login")
@app.route("/edit",methods=["POST"])
def hel():
    if "username" in session:
        course_id = request.form["course_id"]
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM course WHERE id = %s",(course_id,))
            course = cursor.fetchone()
            cursor.execute("SELECT * FROM video WHERE course_id = %s",(course_id,))
            videos = cursor.fetchall()
            cursor.execute("SELECT * FROM pdf WHERE course_id = %s",(course_id,))
            pdfs = cursor.fetchall()
            cursor.execute("SELECT * FROM review WHERE course_id = %s",(course_id,))
            reviews = cursor.fetchall()
            cursor.execute("SELECT * FROM user WHERE id = %s",(session['id'],))
            user = cursor.fetchone()
            connection.commit()
        return render_template("courseedit.html",course = course,user=user,videos=videos,pdfs=pdfs,reviews=reviews)
    else:
        flash("login required")
        return redirect("/login")

@app.route("/review", methods = ["POST","GET"])
def addreview():
    if 'username' in session:
        if request.method == "POST":
            user_id = int(request.form["user_id"])
            comment = request.form["comment"]
            rating = float(request.form["rating"])
            course_id = int(request.form["course_id"])
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE id = %s",(user_id,))
                username = cursor.fetchone()['username']
                sql = f"INSERT INTO review (user_id,username,comment,rating,course_id) VALUES (%s,%s,%s,%s,%s)"
                cursor.execute(sql,(user_id,username,comment,rating,course_id))
                connection.commit()
            s = "/vidandrev/" + str(course_id)
            return redirect(s)
        else:
            return redirect("/home")
    else:
        flash("login required")
        return redirect("/login")

@app.route("/question", methods = ["POST","GET"])
def addquestion():
    if 'username' in session:
        if request.method == "POST":
            comment = request.form["comment"]
            video_id = request.form["video_id"]
            user_id = session['id']
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE id = %s",(user_id,))
                username = cursor.fetchone()['username']
                sql = f"INSERT INTO question (comment,user_id,username,video_id) VALUES (%s,%s,%s,%s)"
                cursor.execute(sql,(comment,user_id,username,video_id))
                connection.commit()
            s = "/ques/" + str(video_id)
            return redirect(s)
        else:
            return render_template(index.html)
@app.route("/answer", methods = ["POST","GET"])
def addanswer():
    if 'username' in session:
        if request.method == "POST":
            comment = request.form["comment"]
            user_id = session['id']
            ques_id = request.form["ques_id"]
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE id = %s",(user_id,))
                username = cursor.fetchone()['username']
                sql = f"INSERT INTO answer (comment,user_id,ques_id,username) VALUES (%s,%s,%s,%s)"
                cursor.execute(sql,(comment,user_id,ques_id,username))
                connection.commit()
            s = "/ans/"+str(ques_id)
            return redirect(s)
        else:
            return redirect("/home")
    else:
        flash("login required")
        return redirect("/login")
#! while deleting a course, its reviews and videos should be deleted too!!!
@app.route("/course/delete/<int:id>")
def deletecourse(id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM video WHERE course_id = ?",(id,))
        videos = cursor.fetchall()
        cursor.execute("SELECT * FROM review WHERE course_id = ?",(id,))
        reviews = cursor.fetchall()
        for review in reviews :
            deletereview(review["id"])
        for video in videos():
            deletevideo(video["id"])
        sql = f"DELETE FROM course WHERE id = %s"
        cursor.execute(sql,id)
        connection.commit()
    return redirect("/")

#! while deleting a video, its questions shsould be deleted too!!!
@app.route("/video/delete/<int:id>")
def deletevideo(id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM question WHERE video_id = %s",(id,))
        questions = cursor.fetchall()
        for question in questions:
            deletequestion(question["id"])
        sql = f"DELETE FROM video WHERE id = %s"
        cursor.execute(sql,(id,))
        connection.commit()
    return redirect("/")

#! while deleting a question, its answers should be deleted too!!!
@app.route("/question/delete/<int:id>")
def deletequestion(id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM answer WHERE ques_id = %s", (id,))
        answers = cursor.fetchall()
        for answer in answers:
            deleteanswer(answer["id"])
        sql = f"DELETE FROM question WHERE id = %s"
        cursor.execute(sql,id)
        connection.commit()
    return redirect("/")

@app.route("/review/delete/<int:id>")
def deletereview(id):
    with connection.cursor() as cursor:
        sql = f"DELETE FROM review WHERE id = %s"
        cursor.execute(sql,id)
        connection.commit()
    return redirect("/")

@app.route("/answer/delete/<int:id>")
def deleteanswer(id):
    with connection.cursor() as cursor:
        sql = f"DELETE FROM answer WHERE id = %s"
        cursor.execute(sql,id)
        connection.commit()
    return redirect("/")

@app.route("/user/delete/<int:id>")
def deleteuser(id):
    with connection.cursor() as cursor:
        sql = f"DELETE FROM user WHERE id = %s"
        cursor.execute(sql,id)
        connection.commit()
    return redirect("/")

@app.route("/editcourse/<int:id>",methods = ["POST","GET"])
def editcourse(id):
    if request.method == "POST":
        with connection.cursor() as cursor:
            name = request.form["name"]
            categoryName = request.form["categoryName"]
            thumbnail = request.form["thumbnail"]
            description = request.form["description"]
            sql = f"UPDATE course SET name = %s, category_name = %s, thumbnail = %s, description = %s WHERE id = %s"
            cursor.execute(sql,(name,categoryName,thumbnail,description,id))
            connection.commit()
    return redirect("/")
@app.route("/editvideo/<int:id>",methods = ["POST","GET"])
def editvideo(id):
    if request.method == "POST":
        with connection.cursor() as cursor:
            videoUrl = request.form["videoUrl"]
            description = request.form["description"]
            sql = f"UPDATE video SET videoUrl = %s, description = %s WHERE id = %s"
            cursor.execute(sql,(videoUrl,description,id))
            connection.commit()
    return redirect("/")

@app.route("/editanswer/<int:id>",methods = ["POST","GET"])
def editanswer(id):
    if request.method == "POST":
        with connection.cursor() as cursor:
            comment = request.form["comment"]
            sql = f"UPDATE answer SET comment = %s WHERE id = %s"
            cursor.execute(sql,(comment,id))
            connection.commit()
    return redirect("/")

@app.route("/editreview/<int:id>",methods = ["POST","GET"])
def editreview(id):
    if request.method == "POST":
        with connection.cursor() as cursor:
            comment = request.form["comment"]
            rating = request.form["rating"]
            sql = f"UPDATE review SET comment = %s, rating = %s WHERE id = %s"
            cursor.execute(sql,(comment,rating,id))
            connection.commit()
    return redirect('/')

@app.route("/courseui/<int:user_id>")
def getCourseFromUserId(user_id):
    with connection.cursor() as cursor:
        courses = cursor.execute("SELECT * FROM course WHERE user_id = %s",(user_id))
        connection.commit()
        return render_template("nextpage.html", courses = courses)

@app.route("/vidandrev/<int:course_id>")
def getVideoAndReview(course_id):
    if 'username' in session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM video WHERE course_id = %s",(course_id))
            videos = cursor.fetchall()
            cursor.execute("SELECT * FROM pdf WHERE course_id = %s",(course_id,))
            pdfs = cursor.fetchall()
            cursor.execute("SELECT * FROM review WHERE course_id = %s",(course_id,))
            reviews = cursor.fetchall()
            cursor.execute("SELECT * FROM course WHERE id = %s",(course_id,))
            course = cursor.fetchone()
            cursor.execute("SELECT * FROM user WHERE id = %s",(course["user_id"],))
            user = cursor.fetchone()
            connection.commit()
        return render_template("course.html", videos = videos,pdfs=pdfs,reviews = reviews,course=course,user=user,u=session["id"],vstring="tab-pane fade show active",rstring="tab-pane fade",vnstring="nav-link active",rnstring="nav-link")
    else:
        flash("login required")
        return redirect("/login")

@app.route("/ques/<int:video_id>")
def getQuestions(video_id):
    if 'username' in session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM question WHERE video_id = %s", (video_id,))
            questions = cursor.fetchall()
            cursor.execute("SELECT * FROM video WHERE id = %s", (video_id,))
            video = cursor.fetchone()
            cursor.execute("SELECT * FROM video WHERE course_id = %s", (video["course_id"],))
            videos = cursor.fetchall()
            connection.commit()
            return render_template("video.html",questions = questions,video = video,videos = videos)
    else:
        flash("login required")
        return redirect("/login")

@app.route("/ans/<int:ques_id>")
def getAnswers(ques_id):
    if 'username' in session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM answer WHERE ques_id = %s", (ques_id,))
            answers = cursor.fetchall()
            cursor.execute("SELECT * FROM question WHERE id = %s",(ques_id,))
            question = cursor.fetchone()
            connection.commit()
            return render_template("example.html", answers = answers,question = question)
    else:
        flash("login required")
        return redirect("/login")
@app.route("/search",methods=["POST"])
def search():
    text = request.form["searched"]
    words = text.split()
    courses1=[]
    with connection.cursor() as cursor:
        # sql = f"SELECT *, MATCH (name,description) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score FROM course WHERE MATCH (name,description) AGAINST (%s IN NATURAL LANGUAGE MODE)"
        # cursor.execute(sql,(text,text))
        # courses = cursor.fetchall()
        # sql = f"SELECT *, MATCH (username,firstname,lastname) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score FROM user WHERE MATCH (username,firstname,lastname) AGAINST (%s IN NATURAL LANGUAGE MODE)"
        # cursor.execute(sql,(text,text))
        # print(type(courses))
        # users = cursor.fetchall()
        # courses1=list(courses)
        # for user in users:
        #     cursor.execute("SELECT * FROM course WHERE user_id = %s",(user["id"],))
        #     courses1 = courses1+list(cursor.fetchall())
        for word in words:
            n = len(word)
            if word[-1] == "." :
                word = word[:-1]
            word = "%"+word+"%"

            sql = f"SELECT * FROM course WHERE name LIKE %s OR category_name LIKE %s OR description LIKE %s"
            cursor.execute(sql,(word,word,word))
            courses = cursor.fetchall()
            sql = f"SELECT * FROM user WHERE username LIKE %s OR firstname LIKE %s OR lastname LIKE %s"
            cursor.execute(sql,(word,word,word))
            print(type(courses))
            users = cursor.fetchall()
            courses1=list(courses)
            for user in users:
                cursor.execute("SELECT * FROM course WHERE user_id = %s",(user["id"],))
                courses1 = courses1+list(cursor.fetchall())
        # cursor.execute("SELECT * FROM course WHERE MATCH (name,description) AGAINST (%s WITH QUERY EXPANSION)",(text,))
        # courses1 = courses1+list(cursor.fetchall())
        connection.commit()
    if 'username' in session:
        return render_template("logsearch.html",courses1=courses1,text = text)
    else:
        return render_template("search.html",courses1=courses1,text = text)
@app.route("/coursefromcategory/<string:categoryName>")
def CourseFromCategory(categoryName):
    if 'username' in session:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM course WHERE category_name = %s", (categoryName,))
            courses = cursor.fetchall()
            print(courses)
            connection.commit()
            return render_template("category.html", courses = courses,category = categoryName)
    else:
        flash("login required")
        return redirect("/login")
@app.route("/coursefromcategoryname/<string:categoryName>")
def getCourseFromCategory(categoryName):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM course WHERE category_name = %s", (categoryName,))
        courses = cursor.fetchall()
        print(courses)
        connection.commit()
        return render_template("indexcategory.html", courses = courses,category = categoryName)

@app.route("/login",methods = ["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM user WHERE username = %s"
            cursor.execute(sql,(username,))
            data = cursor.fetchone()
            if not data :
                flash("Please check your login details and try again")
                return render_template("login.html")
            else:
                if not check_password_hash(data["password"],password) :
                    flash("incorrect password")
                    return render_template("login.html")
            session["loggedin"] = True
            session["id"] = data["id"]
            session["username"] = data["username"]
        return redirect("/home")
    return render_template("login.html")

@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("loggedin"),None
        session.pop('id', None)
        session.pop('username', None)
        return redirect("/")
    else:
        flash("login required")
        return redirect("/login")
@app.route("/signup",methods = ["POST","GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        with connection.cursor() as cursor:
            sql = f"SELECT username FROM user WHERE username = %s"
            cursor.execute(sql,(username,))
            u = cursor.fetchone()
            if u :
                flash("username already exists")
                return render_template("signup.html")
            sql = f"INSERT INTO user (username,password,firstname,lastname,email,isInstructor,about) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(username,generate_password_hash(password),firstname,lastname,email,False,"user.jpeg"))
            connection.commit()
        return redirect("/login")
    return render_template("signup.html")

@app.route("/translateques/<int:videoid>",methods = ["POST"])

def translateq(videoid):
    if "username" in session:
        lang = request.form["language"]
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM question WHERE video_id = %s"
            cursor.execute(sql,(videoid,))
            questions = cursor.fetchall()
            cursor.execute("SELECT * FROM video WHERE id = %s", (videoid,))
            video = cursor.fetchone()
            cursor.execute("SELECT * FROM video WHERE course_id = %s", (video["course_id"],))
            videos = cursor.fetchall()
            connection.commit()
        url = "https://microsoft-translator-text.p.rapidapi.com/translate"
        q = {"to[0]": lang,"api-version":"3.0","profanityAction":"NoAction","textType":"plain"}

        for question in questions:
            payload = [{"Text": question["comment"]}]
            headers = {
                "content-type":"application/json",
                "X-RapidAPI-Key":"43971bdbe4msh984c7472713af7ap11fd60jsnd38c29debc37",
                "X-RapidAPI-host":"microsoft-translator-text.p.rapidapi.com",
                'Accept-Encoding': 'identity'
            }
            proxies = {
                "http": "http://10.10.78.22:3128",
                "https": "http://10.10.78.22:3128"
            }
            response = requests.post(url,proxies=proxies,json=payload, headers=headers,params=q)
            question["comment"] = (response.json())[0]["translations"][0]["text"]
        return render_template("video.html",questions=questions,video=video,videos=videos)
    else:
        flash("login required")
        return redirect("/login")
@app.route("/translateans/<int:quesid>",methods = ["POST"])

def translatea(quesid):
    if "username" in session:
        lang = request.form["language"]
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM answer WHERE ques_id = %s"
            cursor.execute(sql,(quesid,))
            answers = cursor.fetchall()
            cursor.execute("SELECT * FROM question WHERE id = %s",(quesid,))
            question = cursor.fetchone()
            connection.commit()
        url = "https://microsoft-translator-text.p.rapidapi.com/translate"
        q = {"to[0]": lang,"api-version":"3.0","profanityAction":"NoAction","textType":"plain"}

        for answer in answers:
            payload = [{"Text": answer["comment"]}]
            headers = {
                "content-type":"application/json",
                "X-RapidAPI-Key":"43971bdbe4msh984c7472713af7ap11fd60jsnd38c29debc37",
                "X-RapidAPI-host":"microsoft-translator-text.p.rapidapi.com",
                'Accept-Encoding': 'identity'
            }
            proxies = {
                "http": "http://10.10.78.22:3128",
                "https": "http://10.10.78.22:3128"
            }
            response = requests.post(url,proxies=proxies,json=payload, headers=headers,params=q)
            answer["comment"] = (response.json())[0]["translations"][0]["text"]
        return render_template("example.html",answers=answers,question=question)
    else:
        flash("login required")
        return redirect("/login")
@app.route("/translaterev/<int:courseid>",methods = ["POST"])
def translater(courseid):
    if "username" in session:
        lang = request.form["language"]
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM review WHERE course_id = %s"
            cursor.execute(sql,(courseid,))
            reviews = cursor.fetchall()
            cursor.execute("SELECT * FROM video WHERE course_id = %s",(courseid,))
            videos = cursor.fetchall()
            cursor.execute("SELECT * FROM pdf WHERE course_id = %s",(courseid,))
            pdfs = cursor.fetchall()
            cursor.execute("SELECT * FROM course WHERE id = %s",(courseid,))
            course = cursor.fetchone()
            cursor.execute("SELECT * FROM user WHERE id = %s",(course["user_id"],))
            user = cursor.fetchone()
            connection.commit()
            connection.commit()
        url = "https://microsoft-translator-text.p.rapidapi.com/translate"
        q = {"to[0]": lang,"api-version":"3.0","profanityAction":"NoAction","textType":"plain"}

        for review in reviews:
            payload = [{"Text": review["comment"]}]
            headers = {
                "content-type":"application/json",
                "X-RapidAPI-Key":"43971bdbe4msh984c7472713af7ap11fd60jsnd38c29debc37",
                "X-RapidAPI-host":"microsoft-translator-text.p.rapidapi.com",
                'Accept-Encoding': 'identity'
            }
            proxies = {
                "http": "http://10.10.78.22:3128",
                "https": "http://10.10.78.22:3128"
            }
            response = requests.post(url,json=payload, headers=headers,params=q,proxies=proxies,verify=False)
            print(response.json())
            review["comment"] =(response.json())[0]["translations"][0]["text"]
        return render_template("course.html", videos = videos,pdfs=pdfs,reviews = reviews,course=course,user=user,u=session["id"],vstring="tab-pane fade",rstring="tab-pane fade show active",vnstring="nav-link",rnstring="nav-link active")
    else:
        flash("login required")
        return redirect("/login")

@app.route("/addpic", methods =["POST"])
def addpic():
    if "username" in session:
        image = request.files["img"]
        imageData = secure_filename(image.filename)
        image.save(os.path.join(app.config["F"],imageData))
        with connection.cursor() as cursor:
            cursor.execute("UPDATE user SET about = %s WHERE id = %s",(imageData,session["id"]))
            connection.commit()
        return redirect("/profile")
    else:
        flash("login required")
        return redirect("/login")

@app.route("/addpdf",methods=["POST"])
def pdf():
    if "username" in session:
        name = request.form["name"]
        pdfUrl = request.form["pdfUrl"]
        course_id = request.form["course_id"]
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO pdf (name,pdfUrl,course_id) VALUES (%s,%s,%s)",(name,pdfUrl,course_id))
            connection.commit()
            cursor.execute("SELECT * FROM course WHERE id = %s",(course_id,))
            course = cursor.fetchone()
            cursor.execute("SELECT * FROM video WHERE course_id = %s",(course_id,))
            videos = cursor.fetchall()
            cursor.execute("SELECT * FROM pdf WHERE course_id = %s",(course_id,))
            pdfs = cursor.fetchall()
            cursor.execute("SELECT * FROM review WHERE course_id = %s",(course_id,))
            reviews = cursor.fetchall()
            cursor.execute("SELECT * FROM user WHERE id = %s",(session['id'],))
            user = cursor.fetchone()
            connection.commit()
        return render_template("courseedit.html",course = course,user=user,videos=videos,pdfs=pdfs,reviews=reviews)

    else:
        flash("login required")
        return redirect("/login")

@app.route("/mic", methods=["POST"])
def transcribe():
    print("DONE")
    audio = request.form["audio"]
    print(audio)
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {
        "audio_url": audio
    }
    headers = {
        "authorization": "91eddf36eead4ed3851847b64acd50d9",
    }
    response = requests.post(endpoint, json=json, headers=headers)
    return redirect("/home")
@app.route("/haha")
def ha():
    return render_template("file.html")
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
