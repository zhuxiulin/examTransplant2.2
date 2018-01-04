#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('../')
from config import configs
from model import model
import web
import util
from model.orm import *
from config_default import remind_source
from config_default import exampage_source
urls = (
    'Login', 'Login',
    'GetTeacher','GetTeacher',
    'SelectTeacher','SelectTeacher',
    'AddTeacher','AddTeacher',
    'DeleteTeacher','DeleteTeacher',
    'print_exam','print_exam',
    'BatchPrintExam','BatchPrintExam',
    'Remind','Remind',
)
class BatchPrintExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        # str=os.path.abspath("test.docx")
        # str = str.decode('gbk')
        # print str
        classname = model.Class_model.getByPK(params.class_cl_id)
        examname = model.Exam_model.getByPK(params.ex_id)
        directoryName = classname.cl_name + examname.ex_name
        # try:
        # os.mkdir('%s/%s' % (exampage_source, directoryName))

        response = util.Response(status=util.Status.__success__, message =str )
        return util.objtojson(response)
class print_exam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        session = web.ctx.session
        session.student_id = params.student_id
        session.ex_id = params.ex_id
        response = util.Response(status=util.Status.__success__, )
        return util.objtojson(response)

class DeleteTeacher:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        print params
        teacher = model.Teacher_model(**params)
        if teacher.delete():
            response = util.Response(status=util.Status.__success__, )
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__error__, )
            return util.objtojson(response)

class AddTeacher:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        print params
        teacher = model.Teacher_model(**params)
        if teacher.insert():
            response = util.Response(status=util.Status.__success__, )
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__error__, )
            return util.objtojson(response)

class Login:
    def GET(self):
        return web.seeother('/static/exam/TeacherLogin.html',True)
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        session = web.ctx.session
        teacher = model.Teacher_model.getByArgs(tc_id=params.tc_id)
        if teacher[0].tc_password != params.password:
            response = util.Response(status=util.Status.__error__, message="password_error")
            return util.objtojson(response)
        else:
            session.username=params.tc_id
            response = util.Response(status=util.Status.__success__,)
            return util.objtojson(response)

class GetTeacher:
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        try:
            session = web.ctx.session
            username = session.username
            if not username:
                print "not login"
                response = util.Response(status=util.Status.__not_login__, message='4')
                return util.objtojson(response)
        except Exception as e:
            print e
            response = util.Response(status=util.Status.__not_login__, message='4')
            return util.objtojson(response)
        teacher = model.Teacher_model.getByArgs(tc_id=session.username)
        if teacher[0].tc_level == '管理员':
            response = util.Response(status=util.Status.__success__, message='1')
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__success__, message='2')
            return util.objtojson(response)

class SelectTeacher:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        session = web.ctx.session
        currentPage = int(params.currentPage)-1
        count = model.Teacher_model.count()
        if params.tc_name=='' and params.tc_id=='':
            teacher = model.Teacher_model.query('select * from teacher where tc_level\
             = %s order by tc_id limit %s,%s' % ("'"+params.tc_level+"'", currentPage * 10, currentPage * 10 + 9))
            teacher = [model.Teacher_model(**item) for item in teacher]
            page = util.Page(data=teacher, totalRow=count, currentPage=int(params.currentPage), pageSize=10,
                             status=util.Status.__success__, message="未知")
            response = util.Response(status=util.Status.__success__, body=page)
            return util.objtojson(response)
        elif params.tc_name!='' and params.tc_id=='':
            teacher = model.Teacher_model.query('select * from teacher where tc_name \
             like %s and tc_level = %s order by tc_id limit %s,%s'%(params.tc_name,"'"+params.tc_level+"'",currentPage*10,currentPage*10+9))
            teacher = [model.Teacher_model(**item) for item in teacher]
            page = util.Page(data=teacher, totalRow=teacher.__len__(), currentPage=int(params.currentPage), pageSize=10,
                             status=util.Status.__success__, message="未知")
            response = util.Response(status=util.Status.__success__, body=page)
            return util.objtojson(response)
        else:
            teacher = model.Teacher_model.getByPK(params.tc_id)
            page = util.Page(data=teacher, totalRow=1, currentPage=int(params.currentPage), pageSize=10,
                             status=util.Status.__success__, message="未知")
            response = util.Response(status=util.Status.__success__, body=page)
            return util.objtojson(response)

class Remind:
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*")
        f = open('%s/remind.txt'%(remind_source), 'r')
        message = f.read()
        f.close()
        response = util.Response(status=util.Status.__success__, message=message)
        return util.objtojson(response)


app = web.application(urls, globals())
render = web.template.render('template')
if __name__ == '__main__':
    if len(urls) & 1 == 1:
        print "urls error, the size of urls must be even."
    else:
        app.run()