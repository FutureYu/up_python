# coding： utf8
from flask import Flask, render_template, request, make_response, send_from_directory, redirect
import time
import os
import random
import string
import requests
import io
import sys
import pymongo
import re
import threading
import json
from tools import TimeTool

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open("key/config.json", "r") as f:
    ini = json.loads(f.read())
db = pymongo.MongoClient(
    f'mongodb://{ini["db_passwd"]}@{ini["db_ip"]}/', ini["db_port"])["up"]

app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
basedir = os.path.abspath(os.path.dirname(__file__))



class Course:
    @staticmethod
    def GetUploadStamp(stuid, courseName):
        mydoc = db["record"]
        mycol = mydoc.find_one({"_stuid": stuid, "_course_name": courseName})
        # print(stuid, courseName, mycol, flush=True)
        return mycol["_stamp"]

    @staticmethod
    def ChangeCourseMode(stuid, courseName):
        mycoursedoc = db["course"]
        myrecorddoc = db["record"]
        mycoursecol = mycoursedoc.find_one({"_name": courseName})
        mode = mycoursecol["_mode"]
        if stuid:
            status = myrecorddoc.find_one({"_stuid": stuid, "_course_name": courseName})
        else:
            status = None
        timeArray = time.localtime(mycoursecol["_stamp"])
        todayArray = time.localtime(int(time.time()))
        if status == None:
            if mode == 1:
                if time.strftime("%Y-%m-%d", timeArray) == time.strftime("%Y-%m-%d", todayArray):
                    return 21
                else:
                    return 31
            elif mode == 2:
                return 11
            else:
                if mycoursecol["_stamp"] < int(time.time()): 
                    return 10
                elif time.strftime("%Y-%m-%d", timeArray) == time.strftime("%Y-%m-%d", todayArray):
                    return 20
                else:
                    return 30
        else:
            if mode == 1:
                if time.strftime("%Y-%m-%d", timeArray) == time.strftime("%Y-%m-%d", todayArray):
                    return 21
                else:
                    return 31
            elif mode == 2:
                return 11
            else:
                timeArray = time.localtime(mycoursecol["_stamp"])
                todayArray = time.localtime(int(time.time()))
                if mycoursecol["_stamp"] < int(time.time()): 
                    return 11
                elif time.strftime("%Y-%m-%d", timeArray) == time.strftime("%Y-%m-%d", todayArray):
                    return 21
                else:
                    return 31

    @staticmethod
    def GetSlimCourseList(stuid):
        res = []
        mycol = db["course"]
        student = Student()
        student.GetStuDetail(stuid)
        if student.admin:
            mydoc = mycol.find({"_submitable": True, '_stus': stuid}).sort('_stamp', pymongo.DESCENDING).limit(7) 
        else:
            mydoc = mycol.find({"_submitable": True}).sort('_stamp', pymongo.DESCENDING).limit(7) 

        if mydoc == None:
            return res
        else:
            for doc in mydoc:
                print(doc, flush=True)
                endTime = TimeTool.Stamp2FullStr(doc["_stamp"])
                status = Course.ChangeCourseMode(stuid, doc["_name"])
                res.append({"name": doc["_name"], "stamp": doc["_stamp"], "showtime":endTime, "status": status})
            res.reverse()
            return res

    @staticmethod
    def GetSlimDdlList(stuid):
        res = []
        mycol = db["course"]
        student = Student()
        student.GetStuDetail(stuid)
        if student.admin:
            mydoc = mycol.find({"_submitable": False, '_stus': stuid}).sort('_stamp', pymongo.DESCENDING).limit(7) 
        else:
            mydoc = mycol.find({"_submitable": False}).sort('_stamp', pymongo.DESCENDING).limit(7) 

        if mydoc == None:
            return res
        else:
            for doc in mydoc:
                endTime = TimeTool.Stamp2FullStr(doc["_stamp"])
                status = Course.ChangeCourseMode(stuid, doc["_name"])
                res.append({"name": doc["_name"], "stamp": doc["_stamp"], "showtime":endTime, "status": status, "note": doc["_note"]})
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
            self.status = Course.ChangeCourseMode(stuid=None, courseName=self.name)

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
            if mydoc["_stamp"] + 7 * 24 * 60 * 60 < int(time.time()):
                return False
            else:
                if mydoc["_level"] != 1:
                    return False
                return True
    @staticmethod
    def ClearCookies():
        mydoc = db["cookie"] 
        while True:
            print("clear cookies", flush=True)
            mydoc.delete_many({"_stamp": {'$lt': time.time() - 8 * 24 * 60 * 60}}) # 8天
            time.sleep(8 * 24 * 60 * 60)

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
            if mydoc["_stamp"] + 5 * 60 < int(time.time()):
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

    def RenewCookie(self, content):
        mycol = db["cookie"]
        mycol.update_one({"_content": content}, {"$set": {"_stamp": int(time.time())}})
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
        # 免登录，更新cookie
        cookie.RenewCookie(cookie.content)
        nowStamp = int(time.time())
        showtime = TimeTool.Stamp2FullStr(nowStamp)
        resp = make_response(render_template(
            'list.html', stuqq=cookie.stuqq, stuid=cookie.stuid, stuname=cookie.stuname, courses=Course.GetSlimCourseList(cookie.stuid), ddls=Course.GetSlimDdlList(cookie.stuid), stamp=nowStamp, showtime=showtime), 200)
        resp.set_cookie("id", cookie.content, max_age=7 * 24 * 60 * 60)
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
    resp.set_cookie("id", cookie.content, max_age=7 * 24 * 60 * 60)
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

@app.route("/logout", methods=['GET'])
def logout():
    resp = make_response(render_template(
        "success.html", fileName="成功"))
    resp.delete_cookie("id")
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
            if not (re.match(r'([0-9]+(\W+|\_+|[A-Za-z]+))+|([A-Za-z]+(\W+|\_+|\d+))+|((\W+|\_+)+(\d+|\w+))+', newpwd) and len(newpwd) >= 8):
                resp = make_response(render_template(
                    "error.html", errcode="修改失败，密码太过简单", stuqq=student.qq))
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
        return resp
    if not stu.pwd == pwd:
        resp = make_response(render_template(
            "error.html", errcode="错误的学号或密码"), 401)
        return resp
    if not (re.match(r'([0-9]+(\W+|\_+|[A-Za-z]+))+|([A-Za-z]+(\W+|\_+|\d+))+|((\W+|\_+)+(\d+|\w+))+', pwd) and len(pwd) >= 8):
        resp = make_response(render_template(
            "error.html", errcode="密码太过简单，请重设"), 401)
        return resp
    cookie = Cookie()
    cookie.GenerateCookie(stu.stuid, 1)

    if stu.que == "" or stu.ans == "":
        resp = make_response(render_template(
            'bind.html', stuqq=stu.qq, stuid=stu.stuid, stuname=stu.name), 200)
        resp.set_cookie("id", cookie.content, max_age=7 * 24 * 60 * 60)
        return resp


    # 维护中
    # if not stu.admin:
    #     resp = make_response(render_template(
    #         "error.html", errcode="正在维护...请稍后再试"), 401)
    #     return resp
    # 结束维护

    resp = make_response(redirect("/index"))
    resp.set_cookie("id", cookie.content, max_age=7 * 24 * 60 * 60)
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


    # 上传文件
    file_dir = os.path.join(
        basedir, app.config['UPLOAD_FOLDER']) + f"/{courseName}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filenames = os.listdir(file_dir)
    names = []
    for name in filenames:
        if "1617304" in name:
            continue 
        stuid = name.split(" - ")[0]
        filestamp = Course.GetUploadStamp(stuid, courseName)
        changetime = TimeTool.Stamp2FullStr(filestamp)
        names.append({"name": name.split(".")[0], "changetime": changetime})
    names.sort(key=lambda name: name["name"])
    num = len(names)
    if len(names) == 0:
        names = ["还没有人交哦~快快来交"]
    endTime = TimeTool.Stamp2FullStr(course.stamp)
    ext = "，".join(course.ext)
    if cookie.admin:
        return render_template('upload_admin.html', num = num, stuqq=cookie.stuqq, stuname=cookie.stuname, courseName=courseName, names=names, ext=ext, size=course.size, endTime=endTime)
    else:
        return render_template('upload.html', num = num, stuqq=cookie.stuqq, stuname=cookie.stuname, courseName=courseName, names=names, ext=ext, size=course.size, endTime=endTime, upload=course.status >= 20)



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

@app.route('/api/download/<courseName>/<fileName>', methods=['GET'], strict_slashes=False)
def api_download(courseName, fileName):
    cookie = Cookie()
    if not cookie.GetCookieDetail(request.cookies.get("id")):
        resp = make_response(render_template(
            "error.html", errcode="cookie 过期"))
        resp.delete_cookie("id")
        return resp
    course = Course()
    if not course.GetCourseDetail(courseName):
        resp = make_response(render_template(
            "error.html", errcode="文件不存在1"))
        return resp
    mydoc = db["record"]
    stuid = fileName.split("-")[0].strip()
    if cookie.admin:
        print({"_stuid": stuid, "_course_name": courseName}, flush=True)
        mycol = mydoc.find_one({"_stuid": stuid, "_course_name": courseName})
        if mycol == None:
            resp = make_response(render_template(
                "error.html", errcode="文件不存在2"))
            return resp
        fileName = mycol["_file_name"]
    else:
        mycol = mydoc.find_one({"_stuid": cookie.stuid, "_course_name": courseName})
        if mycol == None:
            resp = make_response(render_template(
                "error.html", errcode="文件不存在3"))
            return resp
        fileName = mycol["_file_name"]
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

    if course.status < 20 and not cookie.admin:
        resp = make_response(render_template(
            "error.html", errcode="作业已停止提交"), 200)
        return resp

    file_dir = os.path.join(
        basedir, app.config['UPLOAD_FOLDER']) + f"/{courseName}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f:  # 判断是否是允许上传的文件类型    
        fname = f.filename
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        exterr = True
        for e in course.ext:
            if e == ext:
                exterr = False
        if exterr:
            resp = make_response(render_template(
                "error.html", errcode="文件类型错误", stuqq=cookie.stuqq))
            return resp
            
        if course.note == "":
            new_filename = f"{cookie.stuid} - {cookie.stuname}.{ext}"  # 修改了上传的文件名
        else:
            new_filename = f"{cookie.stuid} - {cookie.stuname} - {course.note}.{ext}"  # 修改了上传的文件名

        requests.get(
            f"https://api.day.app/{ini['msg_key']}/有人交作业了/{courseName}: {new_filename}")
        mydoc = db["record"]
        mycol = mydoc.find_one({"_stuid": cookie.stuid, "_stuname": cookie.stuname, "_course_name": courseName})
        if mycol == None:
            mydoc.insert_one({"_stuid": cookie.stuid, "_stuname": cookie.stuname, "_course_name": courseName, "_file_name": new_filename, "_stamp": int(time.time())})
        else:
            oldfn = os.path.join(file_dir, mycol["_file_name"])
            os.remove(oldfn)
            mydoc.update_one({"_stuid": cookie.stuid, "_stuname": cookie.stuname, "_course_name": courseName}, {"$set": {"_file_name": new_filename, "_stamp": int(time.time())}})
        fn = os.path.join(file_dir, new_filename)
        f.save(fn)  # 保存文件到upload目录
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
    threading.Thread(target=Cookie.ClearCookies).start()
    app.run(debug=False, threaded=True, host="0.0.0.0", port=5000)
