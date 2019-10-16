# coding： utf8
# 24365 
from flask import Flask, render_template, request, make_response, send_from_directory, redirect
import time
import os
import random
import string
import requests
import io
import sys
import pymongo

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
db = pymongo.MongoClient(
    'mongodb://server:tdlm_server123@checkin.nuaaweyes.com/', 27017)["up"]

app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
basedir = os.path.abspath(os.path.dirname(__file__))


class Course:
    @staticmethod
    def GetSlimCourseList():
        res = []
        mycol = db["course"]
        mydoc = mycol.find({"_submitable": True}).sort('_stamp', pymongo.DESCENDING).limit(6) 
        if mydoc == None:
            return res
        else:
            for doc in mydoc:
                timeArray = time.localtime(doc["_stamp"])
                endTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                switch = doc["_switch"]
                if doc["_stamp"] < int(time.time()):
                    switch = False
                res.append({"name": doc["_name"], "stamp": doc["_stamp"], "showtime":endTime, "switch": switch})
            res.reverse()
            return res

    @staticmethod
    def GetSlimDdlList():
        res = []
        mycol = db["course"]
        mydoc = mycol.find({"_submitable": False}).sort('_stamp', pymongo.DESCENDING).limit(6) 
        if mydoc == None:
            return res
        else:
            for doc in mydoc:
                timeArray = time.localtime(doc["_stamp"])
                endTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                switch = doc["_switch"]
                if doc["_stamp"] < int(time.time()):
                    switch = False
                res.append({"name": doc["_name"], "stamp": doc["_stamp"], "showtime":endTime, "note": doc["_note"], "switch": switch})
            res.reverse()
            return res


    def GetCourseDetail(self, course_name):
        mycol = db["course"]
        query = {"_name": course_name}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False
        else:
            self.name = mydoc["_name"]
            self.stamp = mydoc["_stamp"]
            self.ext = mydoc["_ext"]
            self.size = mydoc["_size"]
            self.note = mydoc["_note"]
            self.submitable = mydoc["_submitable"]
            self.switch = mydoc["_switch"]
            if self.stamp < int(time.time()):
                self.switch = False
            return True


class Cookie:
    def GetCookieDetail(self, content):
        if content == None:
            return False
        mycol = db["cookie"]
        query = {"_content": content}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False
        else:
            self.stuid = mydoc["_stuid"]
            self.stuname = mydoc["_stuname"]
            self.stuqq = mydoc["_stuqq"]
            self.content = mydoc["_content"]
            self.level = mydoc["_level"]
            self.stamp = mydoc["_stamp"]
            self.admin = mydoc["_admin"]
            if mydoc["_stamp"] + 360 < int(time.time()):
                return False
            else:
                if mydoc["_level"] != 1:
                    return False
                return True

    def GetTmpCookieDetail(self, content):
        if content == None:
            return False
        mycol = db["cookie"]
        query = {"_content": content}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False
        else:
            self.stuid = mydoc["_stuid"]
            self.stuname = mydoc["_stuname"]
            self.stuqq = mydoc["_stuqq"]
            self.content = mydoc["_content"]
            self.level = mydoc["_level"]
            self.stamp = mydoc["_stamp"]
            self.admin = mydoc["_admin"]
            if mydoc["_stamp"] + 360 < int(time.time()):
                return False
            else:
                if mydoc["_level"] == 1:
                    return False
                return True

    def GenerateCookie(self, stuid, level):
        str_list = [random.choice(string.digits + string.ascii_letters)
                    for i in range(28)]
        random_str = ''.join(str_list)
        stamp = int(time.time())
        mycol1 = db["student"]
        query1 = {"_stuid": stuid}
        mydoc1 = mycol1.find_one(query1)

        mycol = db["cookie"]
        newvalues = {"_stuid": stuid, "_stuname": mydoc1["_name"], "_stuqq": mydoc1["_qq"],
                     "_content": random_str, "_level": level, "_stamp": stamp, "_admin": mydoc1["_admin"]}
        mycol.insert_one(newvalues)
        self.stuid = stuid
        self.stuname = mydoc1["_name"]
        self.stuqq = mydoc1["_qq"]
        self.content = random_str
        self.level = level
        self.stamp = stamp
        self.admin = mydoc1["_admin"]
        return True


class Student:
    def GetStuDetail(self, stuid):
        mycol = db["student"]
        query = {"_stuid": stuid}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False
        else:
            self.stuid = mydoc["_stuid"]
            self.name = mydoc["_name"]
            self.qq = mydoc["_qq"]
            self.pwd = mydoc["_pwd"]
            self.que = mydoc["_que"]
            self.ans = mydoc["_ans"]
            self.admin = mydoc["_admin"]
            return True

    def BindStudent(self, stuid, que, ans):
        mycol = db["student"]
        query = {"_stuid": stuid}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False
        else:
            newvalues = {"$set": {"_ans": ans, "_que": que}}
            mycol.update_one(query, newvalues)
            return True

    def ChangePwd(self, stuid, pwd):
        mycol = db["student"]
        query = {"_stuid": stuid}
        mydoc = mycol.find_one(query)
        if mydoc == None:
            return False
        else:
            newvalues = {"$set": {"_pwd": pwd}}
            mycol.update_one(query, newvalues)
            return True


@app.route("/", methods=['GET'])
@app.route("/index", methods=['GET'])
def index():
    cookie = Cookie()
    if cookie.GetCookieDetail(request.cookies.get("id")):
        print(cookie.admin, flush=True)
        if cookie.admin:
            resp = make_response(render_template(
                'list_admin.html', stuqq=cookie.stuqq, stuid=cookie.stuid, stuname=cookie.stuname, courses=Course.GetSlimCourseList(), ddls=Course.GetSlimDdlList(), stamp=int(time.time())), 200)
            return resp
        else:
            resp = make_response(render_template(
                'list.html', stuqq=cookie.stuqq, stuid=cookie.stuid, stuname=cookie.stuname, courses=Course.GetSlimCourseList(), ddls=Course.GetSlimDdlList(), stamp=int(time.time())), 200)
            return resp

    resp = make_response(render_template('index.html'), 200)
    resp.delete_cookie("id")
    return resp


@app.route("/forget", methods=['GET'])
def forget():
    resp = make_response(render_template('forgetstuid.html'), 200)
    return resp


@app.route("/forgetstuid", methods=['POST'])
def forgetstuid():
    stuid = request.form.get("stuid")
    student = Student()
    cookie = Cookie()
    cookie.GenerateCookie(stuid, 2)
    if not student.GetStuDetail(stuid):
        resp = make_response(render_template(
            "error.html", errcode="错误的学号"), 401)
        return resp

    resp = make_response(render_template(
        'forget.html', que=student.que, stuid=student.stuid, stuqq=student.qq), 200)
    resp.set_cookie("id", cookie.content, max_age=360)
    return resp


@app.route("/forgetpwd", methods=['POST'])
def forgetpwd():
    cookie = Cookie()
    if not cookie.GetTmpCookieDetail(request.cookies.get("id")):
        resp = make_response(render_template(
            "error.html", errcode="cookie 过期"))
        resp.delete_cookie("id")
        return resp

    student = Student()
    student.GetStuDetail(cookie.stuid)
    ans = request.form.get("ans")
    if not ans == student.ans:
        resp = make_response(render_template(
            "error.html", errcode="错误的答案", stuqq=student.qq), 401)
        return resp
    resp = make_response(render_template(
        'reset.html', forget=True, login=True, stuid=student.stuid, stuqq=student.qq), 200)
    return resp


@app.route("/reset", methods=['GET'])
def reset():
    if request.cookies.get("id") == None:
        resp = make_response(render_template(
            'reset.html', forget=False, login=False), 200)
        return resp
    cookie = Cookie()
    if cookie.GetCookieDetail(request.cookies.get("id")):
        resp = make_response(render_template(
            'reset.html', forget=True, login=True), 200)
        return resp
    if cookie.GetTmpCookieDetail(request.cookies.get("id")):
        resp = make_response(render_template(
            'reset.html', forget=True, login=False), 200)
        return resp


@app.route("/resetpwd", methods=['POST'])
def resetpwd():
    stuid = request.form.get("stuid")
    oldpwd = request.form.get("oldpwd")
    newpwd = request.form.get("newpwd")
    newpwd2 = request.form.get("newpwd2")

    if request.cookies.get("id") == None:
        student = Student()
        student.GetStuDetail(stuid)
        if student.pwd == oldpwd and newpwd == newpwd2 != "":
            if not student.ChangePwd(student.stuid, newpwd):
                resp = make_response(render_template(
                    "error.html", errcode="修改失败", stuqq=student.qq))
                resp.delete_cookie("id")
                return resp
            resp = make_response(render_template(
                "success.html", fileName="修改成功"), 200)
            resp.delete_cookie("id")
            return resp
        resp = make_response(render_template(
            "error.html", errcode="旧密码错误或两次输入不一致"))
        resp.delete_cookie("id")
        return resp

    cookie = Cookie()
    if cookie.GetCookieDetail(request.cookies.get("id")):
        student = Student()
        student.GetStuDetail(cookie.stuid)
        if newpwd == newpwd2:
            if not student.ChangePwd(student.stuid, newpwd):
                resp = make_response(render_template(
                    "error.html", errcode="修改失败", stuqq=student.qq))
                resp.delete_cookie("id")
                return resp
            resp = make_response(render_template(
                "success.html", fileName="修改成功"), 200)
            resp.delete_cookie("id")
            return resp
        resp = make_response(render_template(
            "error.html", errcode="两次输入不一致"))
        resp.delete_cookie("id")
        return resp
    if cookie.GetTmpCookieDetail(request.cookies.get("id")):
        student = Student()
        student.GetStuDetail(cookie.stuid)
        if newpwd == newpwd2:
            if not student.ChangePwd(student.stuid, newpwd):
                resp = make_response(render_template(
                    "error.html", errcode="修改失败", stuqq=student.qq))
                resp.delete_cookie("id")
                return resp
            resp = make_response(render_template(
                "success.html", fileName="修改成功"), 200)
            resp.delete_cookie("id")
            return resp
        resp = make_response(render_template(
            "error.html", errcode="两次输入不一致"))
        resp.delete_cookie("id")
        return resp


@app.route("/bind", methods=['POST'])
def bind():
    cookie = Cookie()
    if not cookie.GetCookieDetail(request.cookies.get("id")):
        resp = make_response(render_template(
            "error.html", errcode="cookie 过期"))
        resp.delete_cookie("id")
        return resp

    que = request.form.get("que")
    ans = request.form.get("ans")
    if que == "" or ans == "":
        resp = make_response(render_template(
            "error.html", errcode="错误的问题或回答", stuqq=cookie.stuqq), 401)
        resp.delete_cookie("id")
        return resp
    student = Student()
    if student.BindStudent(cookie.stuid, que, ans):
        resp = make_response(render_template(
            "success.html", fileName="设置成功", stuqq=cookie.stuqq), 200)
        return resp
    resp = make_response(render_template(
        "error.html", errcode="错误的学号或密码", stuqq=cookie.stuqq), 401)
    return resp


@app.route("/login", methods=['POST'])
def login():
    stuid = request.form.get("stuid")
    pwd = request.form.get("pwd")
    stu = Student()
    if not stu.GetStuDetail(stuid):
        resp = make_response(render_template(
            "error.html", errcode="错误的学号或密码"), 401)
    if not stu.pwd == pwd:
        resp = make_response(render_template(
            "error.html", errcode="错误的学号或密码"), 401)
    if pwd == "":
        resp = make_response(render_template(
            "error.html", errcode="密码不能为空"), 401)
    # if not stu.pwd == pwd == "":
    #     resp = make_response(render_template(
    #         "error.html", errcode="密码不能为空"), 401)
        return resp
    cookie = Cookie()
    cookie.GenerateCookie(stu.stuid, 1)
    if stu.que == "" or stu.ans == "":
        resp = make_response(render_template(
            'bind.html', stuqq=stu.qq, stuid=stu.stuid, stuname=stu.name), 200)
        resp.set_cookie("id", cookie.content, max_age=360)
        return resp

    resp = make_response(redirect("/index"))
    resp.set_cookie("id", cookie.content, max_age=360)
    return resp


@app.route('/upload/<courseName>')
def upload(courseName):
    cookie = Cookie()
    if not cookie.GetCookieDetail(request.cookies.get("id")):
        resp = make_response(render_template(
            "error.html", errcode="cookie 过期"))
        resp.delete_cookie("id")
        return resp

    course = Course()
    if not course.GetCourseDetail(courseName):
        resp = make_response(render_template(
            "error.html", errcode="作业不存在", stuqq=cookie.stuqq), 404)
        return resp
    if int(time.time()) > course.stamp and not cookie.admin:
        resp = make_response(render_template(
            "error.html", errcode="作业已停止提交"), 200)
        return resp

    # 上传文件
    file_dir = os.path.join(
        basedir, app.config['UPLOAD_FOLDER']) + f"/{courseName}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filenames = os.listdir(file_dir)
    names = []
    for i, name in enumerate(filenames):
        filestamp = os.stat(f"{file_dir}/{filenames[i]}").st_mtime
        timeArray = time.localtime(filestamp)
        changetime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        names.append({"name": name.split(".")[0], "changetime": changetime})
    names.sort(key=lambda name: name["name"])
    num = len(names)
    if len(names) == 0:
        names = ["还没有人交哦~快快来交"]
    timeArray = time.localtime(course.stamp)
    endTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    if cookie.admin:
        return render_template('upload_admin.html', num = num, stuqq=cookie.stuqq, stuname=cookie.stuname, courseName=courseName, names=names, ext=course.ext, size=course.size, endTime=endTime)
    else:
        return render_template('upload.html', num = num, stuqq=cookie.stuqq, stuname=cookie.stuname, courseName=courseName, names=names, ext=course.ext, size=course.size, endTime=endTime)


@app.route('/api/download/all/<courseName>', methods=['GET'], strict_slashes=False)
def api_download_all(courseName):
    cookie = Cookie()
    if not cookie.GetCookieDetail(request.cookies.get("id")) and cookie.admin:
        resp = make_response(render_template(
            "error.html", errcode="cookie 过期"))
        resp.delete_cookie("id")
        return resp
    course = Course()
    if not course.GetCourseDetail(courseName):
        resp = make_response(render_template(
            "error.html", errcode="文件不存在"))
        return resp
    file_dir = os.path.join(
        basedir, app.config['UPLOAD_FOLDER']) + f"/{courseName}"
    os.system(f"cd {file_dir} && zip -q -r '1617304 - {courseName}.zip' * -x '1617304 - {courseName}.zip'")

    fileName = f"1617304 - {courseName}.zip"
    
    response = make_response(send_from_directory(
        file_dir, fileName, as_attachment=True, attachment_filename=fileName))
    return response

@app.route('/api/download/<courseName>/<stuid>', methods=['GET'], strict_slashes=False)
def api_download(courseName, stuid):
    cookie = Cookie()
    if not cookie.GetCookieDetail(request.cookies.get("id")):
        resp = make_response(render_template(
            "error.html", errcode="cookie 过期"))
        resp.delete_cookie("id")
        return resp
    course = Course()
    if not course.GetCourseDetail(courseName):
        resp = make_response(render_template(
            "error.html", errcode="文件不存在"))
        return resp
    if cookie.admin:
        fileName = stuid + "." + course.ext
    else:
        fileName = cookie.stuid + " - " + cookie.stuname + "." + course.ext
    file_dir = os.path.join(
        basedir, app.config['UPLOAD_FOLDER']) + f"/{courseName}"
    response = make_response(send_from_directory(
        file_dir, fileName, as_attachment=True, attachment_filename=fileName))
    return response


@app.route('/api/upload/<courseName>', methods=['POST'], strict_slashes=False)
def api_upload(courseName):
    cookie = Cookie()
    if not cookie.GetCookieDetail(request.cookies.get("id")):
        resp = make_response(render_template(
            "error.html", errcode="cookie 过期"))
        resp.delete_cookie("id")
        return resp

    course = Course()
    if not course.GetCourseDetail(courseName):
        resp = make_response(render_template(
            "error.html", errcode="作业名错误", stuqq=cookie.stuqq))
        return resp
    print(123, flush=True)
    file_dir = os.path.join(
        basedir, app.config['UPLOAD_FOLDER']) + f"/{courseName}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f:  # 判断是否是允许上传的文件类型    
        fname = f.filename
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        if not course.ext == ext:
            resp = make_response(render_template(
                "error.html", errcode="文件类型错误", stuqq=cookie.stuqq))
            return resp
        print(87891, flush=True)
        # size = len(f.read())
        # if not course.size <= size * 1024 * 1024:
        #     resp = make_response(render_template(
        #         "error.html", errcode="文件过大", stuqq=cookie.stuqq))
        #     return resp
        new_filename = cookie.stuid + " - " + cookie.stuname + '.' + ext  # 修改了上传的文件名
        fn = os.path.join(file_dir, new_filename)
        # f.seek(0,0)
        f.save(fn)  # 保存文件到upload目录
        requests.get(
            f"https://api.day.app/YHZ2mLaZaGjRXP5mUNTRJG/有人交作业了/{courseName}: {new_filename}")
        return render_template("success.html", stuqq=cookie.stuqq, fileName=f"{new_filename} 上传成功")
    else:
        return render_template("error.html", errcode="上传失败", stuqq=cookie.stuqq)


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", errcode="页面不存在")


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", errcode="页面错误，请稍后再试")


if __name__ == '__main__':
    app.run(debug=True, threaded=True, host="0.0.0.0", port=5000)
