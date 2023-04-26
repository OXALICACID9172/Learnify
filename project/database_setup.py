import csv
import random
import flask
from werkzeug.security import generate_password_hash
file = open("hello (6).csv","r", encoding="utf8")
courses = list(csv.reader(file, delimiter=","))
file.close()
file = open("NationalNames.csv","r", encoding="utf8")
firstnames = list(csv.reader(file, delimiter=","))
file.close()
file = open("usernames.csv","r", encoding="utf8")
usernames = list(csv.reader(file, delimiter=","))
file.close()
file = open("passwors.csv","r", encoding="utf8")
passwords = list(csv.reader(file, delimiter=","))
file.close()
lastnames = ["smith","anderson","johnson","williams"]
file = open("CommentsMarch2018.csv","r", encoding="utf8")
comments = list(csv.reader(file, delimiter=","))
file.close()

categories = ["Web Development","Game Development", "Organic Chemistry","Inorganic Chemistry","Physical Chemistry","Biochemistry","3D and Animation","Analytical Chemistry","Anatomy","Cryptocurrency and Blockchain","Financial Modeling and Analysis", "Graphic Design and Illustration","Instruments","Investing and Trading","Microbiology","Music software","Parasitology","Programming Languages","Taxonomy","Vocal","Web Design"]
import pymysql
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='d3f1d717',
                             database='learnify',
                             cursorclass=pymysql.cursors.DictCursor)

def setup():
  # with connection:
    with connection.cursor() as cursor:
      cursor.execute("""CREATE TABLE IF NOT EXISTS `user` (
             `id` int NOT NULL AUTO_INCREMENT,
             `username` varchar(255) NOT NULL,
             `firstname` varchar(255) DEFAULT NULL,
             `lastname` varchar(255) DEFAULT NULL,
             `email` varchar(255) DEFAULT NULL,
             `password` varchar(255) DEFAULT NULL,
             `about` varchar(255) DEFAULT NULL,
             `isInstructor` bool DEFAULT false,
             PRIMARY KEY (`id`),
             UNIQUE KEY  (`username`)
           )""")
      cursor.execute("""CREATE TABLE IF NOT EXISTS `category` (
        `id` int NOT NULL AUTO_INCREMENT,
        `name` varchar(255) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE KEY (`name`))""")

      cursor.execute("""CREATE TABLE IF NOT EXISTS `course` (
        `id` int NOT NULL AUTO_INCREMENT,
        `name` varchar(255) NOT NULL,
        `category_name` varchar(255) NOT NULL,
        `user_id` int NOT NULL,
        `thumbnail` varchar(255) DEFAULT NULL,
        `description` varchar(511) DEFAULT NULL,
        `rating` float DEFAULT NULL,
        `numofreviews` int DEFAULT NULL,
        PRIMARY KEY (`id`),
        FOREIGN KEY (`category_name`) REFERENCES `category` (`name`),
        FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
      )""")
      cursor.execute("""CREATE TABLE IF NOT EXISTS `video` (
              `id` int NOT NULL AUTO_INCREMENT,
              `name` varchar(255) NOT NULL,
              `videoUrl` varchar(1023) NOT NULL,
              `description` varchar(2047) NOT NULL,
              `course_id` int NOT NULL,
              PRIMARY KEY (`id`),
              FOREIGN KEY (`course_id`) REFERENCES `course` (`id`)
            )""")
      cursor.execute("""CREATE TABLE IF NOT EXISTS `question` (
        `id` int NOT NULL AUTO_INCREMENT,
        `comment` varchar(1023) NOT NULL,
        `user_id` int  NOT NULL,
        `username` varchar(255) NOT NULL,
        `video_id` int NOT NULL,
        PRIMARY KEY (`id`),
        FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
        FOREIGN KEY (`username`) REFERENCES `user` (`username`),
        FOREIGN KEY (`video_id`) REFERENCES `video`(`id`)
      )""")

      cursor.execute("""CREATE TABLE IF NOT EXISTS `review` (
        `id` int NOT NULL AUTO_INCREMENT,
        `user_id` int NOT NULL,
        `username` varchar(255) NOT NULL,
        `comment` varchar(1023) DEFAULT NULL,
        `rating` float DEFAULT NULL,
        `course_id` int NOT NULL,
        PRIMARY KEY(`id`),
        FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
        FOREIGN KEY (`username`) REFERENCES `user` (`username`),
        FOREIGN KEY (`course_id`) REFERENCES `course` (`id`)
      )""")
      cursor.execute("""CREATE TABLE IF NOT EXISTS `answer` (
             `id` int NOT NULL AUTO_INCREMENT,
             `comment` varchar(1023) DEFAULT NULL,
             `user_id` int  NOT NULL,
             `username` varchar(255) NOT NULL,
             `ques_id` int NOT NULL,
             PRIMARY KEY (`id`),
             FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
              FOREIGN KEY (`username`) REFERENCES `user` (`username`),
             FOREIGN KEY (`ques_id`) REFERENCES `question`(`id`)
           )""")


      cursor.execute("""CREATE TABLE IF NOT EXISTS `pdf` (
                    `id` int NOT NULL AUTO_INCREMENT,
                    `name` varchar(255) NOT NULL,
                    `pdfUrl` varchar(255) NOT NULL,
                    `course_id` int NOT NULL,
                    PRIMARY KEY (`id`),
                    FOREIGN KEY (`course_id`) REFERENCES `course` (`id`)
                  )""")
# print(courses[0])
# setup()
# def addcourse():
#    for course in courses:
#       thumbnail = course[0]
#       name = course[1]
print(len(categories))
print("usernames: ",len(usernames),"firstnames: ",len(firstnames),"lastnames: ",len(lastnames),"passwords: ",len(passwords))
def addusers():
   for i in range(4000):
      print(i)
      username = usernames[i][0]
      password = generate_password_hash(passwords[i][0])
      firstname = firstnames[i+1][1]
      about=""
      b = random.randint(0,3)
      lastname = lastnames[b]
      with connection.cursor() as cursor:
        sql = f"INSERT INTO user (username,password,firstname,lastname,email,isInstructor,about) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,(username,password,firstname,lastname,"",False,about))
        connection.commit()
def addcourses():
    for i in range(len(courses)):
        print(i)
        name = courses[i][1]
        thumbnail = courses[i][0]
        b = random.randint(0,20)
        categoryName = categories[b]
        rating=0
        description = comments[i][3]
        if(len(description)>500):
           description=description[:499]
        c = random.randint(1,4000)
        user_id = c
        with connection.cursor() as cursor:
            sql = f"INSERT INTO course (name,category_name,user_id,thumbnail,description,rating,numofreviews) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (name, categoryName,user_id,thumbnail,description,0,0))
            connection.commit()
def addreviews():
   for i in range(6000):
      print(i)
      user_id=random.randint(1,4000)
      username=usernames[user_id-1][0]
      comment=comments[600+i][3]
      if(len(comment)>1000):
         comment=comment[:999]
      rating=random.randint(1,5)
      course_id=random.randint(1,537)
      with connection.cursor() as cursor:
            sql = f"INSERT INTO review (user_id,username,comment,rating,course_id) VALUES (%s,%s,%s,%s,%s)"
            cursor.execute(sql,(user_id,username,comment,rating,course_id))
            connection.commit()
def addvideos():
   for i in range(len(courses)):
      course=courses[i]
      j=3
      print(i)
      while(j<len(course) and course[j]!=""):
         description=course[j+1]
         if(len(description)>2000):
            description=description[:1999]
         name=course[j+2]
         videoUrl=course[j+3]
         course_id=i+1
         with connection.cursor() as cursor:
            sql = f"INSERT INTO video (videoUrl,description,name,course_id) VALUES (%s,%s,%s,%s)"
            cursor.execute(sql,(videoUrl,description,name,course_id))
            connection.commit()
         j+=4
def addquestions():
   for i in range(10000):
      print(i)
      comment=comments[8000+i][3]
      if(len(comment)>1000):
         comment=comment[:999]
      user_id=random.randint(1,4000)
      username=usernames[user_id-1][0]
      video_id=random.randint(1,1000)
      with connection.cursor() as cursor:
            sql = f"INSERT INTO question (comment,user_id,username,video_id) VALUES (%s,%s,%s,%s)"
            cursor.execute(sql,(comment,user_id,username,video_id))
            connection.commit()
   for i in range(20000):
      print(i)
      comment=comments[18000+i][3]
      if(len(comment)>1000):
          comment=comment[:999]
      user_id=random.randint(1,4000)
      username=usernames[user_id-1][0]
      video_id=random.randint(1000,20695)
      with connection.cursor() as cursor:
            sql = f"INSERT INTO question (comment,user_id,username,video_id) VALUES (%s,%s,%s,%s)"
            cursor.execute(sql,(comment,user_id,username,video_id))
            connection.commit()
    
def addanswers():
   for i in range(100000):
      print(i)
      user_id=random.randint(1,4000)
      username=usernames[user_id-1][0]
      comment=comments[50000+i][3]
      if(len(comment)>1000):
          comment=comment[:999]
      ques_id=random.randint(1,30000)
      with connection.cursor() as cursor:
            sql = f"INSERT INTO answer (comment,user_id,username,ques_id) VALUES (%s,%s,%s,%s)"
            cursor.execute(sql,(comment,user_id,username,ques_id))
            connection.commit()
def addcategories():
    for category in categories:
        with connection.cursor() as cursor:
            sql = f"INSERT INTO category (name) VALUES (%s)"
            cursor.execute(sql,(category,))
            connection.commit()
# setup()
# addcategories()
# addcourses()

addreviews()
addvideos()
addquestions()
addanswers()
