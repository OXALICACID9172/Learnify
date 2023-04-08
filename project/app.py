from flask import Flask,render_template,request,redirect,url_for,session,flash

import pymysql
import base64

from werkzeug.security import generate_password_hash, check_password_hash

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='d3f1d717',
                             database='LEARNIFY',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)

app.secret_key = '^$*Hdd68*f'

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
            cursor.execute("SELECT * FROM course")
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
        cursor.execute("SELECT * FROM course")
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
                sql = f"INSERT INTO course (name,category_name,user_id,thumbnail,description,rating) VALUES (%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (courseName, categoryName,user_id,thumbnail,description,0))
                cursor.execute("SELECT * FROM course WHERE id = %s",(cursor.lastrowid,))
                course = cursor.fetchone()
                cursor.execute("SELECT * FROM user WHERE id = %s",(user_id,))
                user = cursor.fetchone()
                connection.commit()
            return render_template("courseedit.html",course = course,user=user)
        else:
            return render_template("createcourse.html",u=session["id"])
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
                cursor.execute("SELECT * FROM user WHERE id = %s",(session['id'],))
                user = cursor.fetchone()
                connection.commit()
            return render_template("courseedit.html",course = course,user=user,videos=videos)
        else:
            return redirect("/home")
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
            user_id = request.form["user_id"]
            video_id = request.form["video_id"]
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE id = %s",(user_id,))
                username = cursor.fetchone()['username']
                sql = f"INSERT INTO question (comment,user_id,username,video_id) VALUES (%s,%s,%s,%s)"
                cursor.execute(sql,(comment,user_id,username,video_id))
                connection.commit()
            return redirect("/")
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
                sql=f"SELECT * FROM question WHERE id = %s"
                cursor.execute(sql,(ques_id,))
                question = cursor.fetchone()
                connection.commit()
            s = "/ques/"+str(question['video_id'])
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
            sql = f"UPDATE course SET name = %s, category_name = %s, thumbnail = %s, description = %s"
            cursor.execute(sql,(name,categoryName,thumbnail,description))
            connection.commit()
    return redirect("/")
@app.route("/editvideo/<int:id>",methods = ["POST","GET"])
def editvideo(id):
    if request.method == "POST":
        with connection.cursor() as cursor:
            videoUrl = request.form["videoUrl"]
            description = request.form["description"]
            sql = f"UPDATE video SET videoUrl = %s, description = %s"
            cursor.execute(sql,(videoUrl,description))
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
            cursor.execute("SELECT * FROM review WHERE course_id = %s",(course_id,))
            reviews = cursor.fetchall()
            cursor.execute("SELECT * FROM course WHERE id = %s",(course_id,))
            course = cursor.fetchone()
            cursor.execute("SELECT * FROM user WHERE id = %s",(course["user_id"],))
            user = cursor.fetchone()
            connection.commit()
        return render_template("course.html", videos = videos,reviews = reviews,course=course,user=user,u=session["id"])
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
            cursor.execute(sql,(username,generate_password_hash(password),firstname,lastname,email,False,""))
            connection.commit()
        return redirect("/login")
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)