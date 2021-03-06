#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.append('../')
from config import configs
from model import model
import web
import util
import datetime
import time
import thread
from model.orm import *
urls = (
    'Login', 'Login',
    'SelectExamQuestionById','SelectExamQuestionById',
    'SaveExam','SaveExam',
    'gettime','gettime',
    'HandInExam','HandInExam',
    'recover_exam','recover_exam',
    'new_exam','new_exam',
)

# 练习模式重新抽题
class new_exam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        session = web.ctx.session
        information_data = model.Information_model.query('SELECT * FROM information WHERE \
                            student_st_id=%s and exam_ex_id=%s' % (session.student_id, session.ex_id))
        information = model.Information_model(**information_data[0])
        information.in_state = '1'
        information.inscore = -1
        exam = model.Exam_model.getByArgs(ex_id=session.ex_id)
        delta = datetime.timedelta(minutes=exam[0].ex_duration)
        now = datetime.datetime.now()
        end_time = now + delta
        information.in_endtime = end_time.strftime('%Y-%m-%d %H:%M:%S')
        information.update()
        db.delete('exam_question', where="information_in_id = $information_in_id", vars={'information_in_id': information.in_id, })
        Extract.extract()
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)
# 练习模式不抽题,继续做题
class recover_exam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        session = web.ctx.session
        information_data = model.Information_model.query('SELECT * FROM information WHERE \
                            student_st_id=%s and exam_ex_id=%s' % (session.student_id, session.ex_id))
        information = model.Information_model(**information_data[0])
        now = datetime.datetime.now()
        exam = model.Exam_model.getByArgs(ex_id=session.ex_id)
        delta = datetime.timedelta(minutes=exam[0].ex_duration)
        end_time = now + delta
        information.in_endtime = end_time.strftime('%Y-%m-%d %H:%M:%S')
        information.in_state = '1'
        information.update()
        response = util.Response(status=util.Status.__success__,)
        return util.objtojson(response)

class Extract:
    @classmethod
    def extract(cls):
        session = web.ctx.session
        information = model.Information_model.query('select * from information where exam_ex_id=%s\
             and student_st_id = %s'%(session.ex_id,session.student_id))
        information = model.Information_model(**information[0])
        lists = model.Strategy_term_model.getByArgs(strategy_sg_id=information['sg_id'])
        for strategy_term in lists:
            if strategy_term.sm_type == 'choice':
                if strategy_term.sm_knowledge == 0:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and \
                               qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'choice' + "'",
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                else:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                               = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'choice' + "'",
                                                         strategy_term.sm_knowledge,
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high,
                                                         strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                for question in result:
                    qt_id = question.qt_id
                    # 添加exam_questions
                    exam_question = model.Exam_question_model()
                    exam_question.information_in_id = information['in_id']
                    exam_question['qt_id'] = qt_id
                    exam_question.eq_qt_type = question.qt_type
                    exam_question.eq_pre_score = strategy_term.sm_score
                    exam_question.eq_answer = "答案"
                    eq_id = exam_question.insertBackid()
            if strategy_term.sm_type == 'judge':
                if strategy_term.sm_knowledge == 0:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and \
                               qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'judge' + "'",
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                else:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                               = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'judge' + "'",
                                                         strategy_term.sm_knowledge,
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high,
                                                         strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                for question in result:
                    # 添加exam_question
                    exam_question = model.Exam_question_model()
                    exam_question.information_in_id = information['in_id']
                    exam_question.qt_id = question.qt_id
                    exam_question.eq_qt_type = question.qt_type
                    exam_question.eq_pre_score = strategy_term.sm_score
                    exam_question.eq_answer = "答案"
                    eq_id = exam_question.insertBackid()
            if strategy_term.sm_type == 'filla':
                if strategy_term.sm_knowledge == 0:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and \
                               qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'filla' + "'",
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                else:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                               = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'filla' + "'",
                                                         strategy_term.sm_knowledge,
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high,
                                                         strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                for question in result:
                    # 添加exam_question
                    exam_question = model.Exam_question_model()
                    exam_question.information_in_id = information['in_id']
                    exam_question.qt_id = question.qt_id
                    exam_question.eq_qt_type = question.qt_type
                    exam_question.eq_pre_score = strategy_term.sm_score
                    exam_question.eq_answer = "答案"
                    eq_id = exam_question.insertBackid()
            if strategy_term.sm_type == 'fillb':
                if strategy_term.sm_knowledge == 0:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and \
                               qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'fillb' + "'",
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                else:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                               = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'fillb' + "'",
                                                         strategy_term.sm_knowledge,
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high,
                                                         strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                for question in result:
                    fillb_data = model.Fillb_model.getByPK(question.qt_id)
                    # 统计空数量
                    count = fillb_data.fb_pre_coding.count("&&&")
                    count = count / 2

                    eq_id_data = []
                    while count > 0:
                        count = count - 1;
                        # 添加exam_question
                        exam_question = model.Exam_question_model()
                        exam_question.information_in_id = information['in_id']
                        exam_question.qt_id = question.qt_id
                        exam_question.eq_qt_type = question.qt_type
                        exam_question.eq_pre_score = strategy_term.sm_score
                        exam_question.eq_answer = "答案"
                        eq_id = exam_question.insertBackid()
            if strategy_term.sm_type == 'coding':
                if strategy_term.sm_knowledge == 0:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and \
                               qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'coding' + "'",
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high, strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                else:
                    result = model.Question_model.query('select * from question where qt_id \
                              in (select question_qt_id from questions_bank_has_question where \
                               questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                               = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                        (strategy_term.qb_id, "'" + 'coding' + "'",
                                                         strategy_term.sm_knowledge,
                                                         strategy_term.sm_difficulty_low,
                                                         strategy_term.sm_difficulty_high,
                                                         strategy_term.sm_number))
                    result = [model.Question_model(**item) for item in result]
                for question in result:
                    # 添加exam_question
                    exam_question = model.Exam_question_model()
                    exam_question.information_in_id = information['in_id']
                    exam_question.qt_id = question.qt_id
                    exam_question.eq_qt_type = question.qt_type
                    exam_question.eq_pre_score = strategy_term.sm_score
                    exam_question.eq_answer = "答案"
                    eq_id = exam_question.insertBackid()
        response = util.Response(status=util.Status.__success__, )
        return util.objtojson(response)

class Login:
    def GET(self):
        print "login"
        return web.seeother('/static/exam/login.html',True)
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        # 接收参数
        params = web.input()
        session = web.ctx.session
        information_data= model.Information_model.query('select * from information where exam_ex_id=%s\
             and student_st_id = %s'%(params.ex_id,params.student_id))

        if information_data:
            information = model.Information_model(**information_data[0])
            exam = model.Exam_model.getByArgs(ex_id=params.ex_id)
            if params.password!=exam[0].ex_login_password :
                response = util.Response(status=util.Status.__error__, message="password_error")
                return util.objtojson(response)
            if information.in_state == '0':
                information.in_temp_ip = web.ctx.ip
                if information.update():
                    information.in_state = '1'
                    information.in_ip = information.in_temp_ip
                    now = datetime.datetime.now()
                    delta = datetime.timedelta(minutes=exam[0].ex_duration)
                    end_time = now + delta
                    information.in_endtime = end_time.strftime('%Y-%m-%d %H:%M:%S')
                    print information
                    information.update()
                    # 存储session
                    web.setcookie('system_mangement', '', 120)
                    session.student_id = params.student_id
                    session.ex_id = params.ex_id

                    lists = model.Strategy_term_model.getByArgs(strategy_sg_id=information['sg_id'])
                    for strategy_term in lists:
                        if strategy_term.sm_type == 'choice':
                            if strategy_term.sm_knowledge==0:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and \
                                           qt_diffculty between %s and %s order by rand() limit %s' % \
                                           (strategy_term.qb_id, "'" + 'choice' + "'",strategy_term.sm_difficulty_low,
                                            strategy_term.sm_difficulty_high,strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            else:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                                           = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                                    (strategy_term.qb_id, "'" + 'choice' + "'",
                                                                     strategy_term.sm_knowledge,
                                                                     strategy_term.sm_difficulty_low,
                                                                     strategy_term.sm_difficulty_high,
                                                                     strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            for question in result:
                                qt_id = question.qt_id
                                # 添加exam_questions
                                exam_question = model.Exam_question_model()
                                exam_question.information_in_id = information['in_id']
                                exam_question['qt_id'] = qt_id
                                exam_question.eq_qt_type = question.qt_type
                                exam_question.eq_pre_score = strategy_term.sm_score
                                exam_question.eq_answer = "答案"
                                eq_id = exam_question.insertBackid()
                        if strategy_term.sm_type == 'judge':
                            if strategy_term.sm_knowledge==0:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and \
                                           qt_diffculty between %s and %s order by rand() limit %s' % \
                                           (strategy_term.qb_id, "'" + 'judge' + "'",strategy_term.sm_difficulty_low,
                                            strategy_term.sm_difficulty_high,strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            else:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                                           = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                                    (strategy_term.qb_id, "'" + 'judge' + "'",
                                                                     strategy_term.sm_knowledge,
                                                                     strategy_term.sm_difficulty_low,
                                                                     strategy_term.sm_difficulty_high,
                                                                     strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            for question in result:
                                # 添加exam_question
                                exam_question = model.Exam_question_model()
                                exam_question.information_in_id = information['in_id']
                                exam_question.qt_id = question.qt_id
                                exam_question.eq_qt_type = question.qt_type
                                exam_question.eq_pre_score = strategy_term.sm_score
                                exam_question.eq_answer = "答案"
                                eq_id = exam_question.insertBackid()
                        if strategy_term.sm_type == 'filla':
                            if strategy_term.sm_knowledge==0:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and \
                                           qt_diffculty between %s and %s order by rand() limit %s' % \
                                           (strategy_term.qb_id, "'" + 'filla' + "'",strategy_term.sm_difficulty_low,
                                            strategy_term.sm_difficulty_high,strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            else:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                                           = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                                    (strategy_term.qb_id, "'" + 'filla' + "'",
                                                                     strategy_term.sm_knowledge,
                                                                     strategy_term.sm_difficulty_low,
                                                                     strategy_term.sm_difficulty_high,
                                                                     strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            for question in result:
                                # 添加exam_question
                                exam_question = model.Exam_question_model()
                                exam_question.information_in_id = information['in_id']
                                exam_question.qt_id = question.qt_id
                                exam_question.eq_qt_type = question.qt_type
                                exam_question.eq_pre_score = strategy_term.sm_score
                                exam_question.eq_answer = "答案"
                                eq_id = exam_question.insertBackid()
                        if strategy_term.sm_type == 'fillb':
                            if strategy_term.sm_knowledge==0:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and \
                                           qt_diffculty between %s and %s order by rand() limit %s' % \
                                           (strategy_term.qb_id, "'" + 'fillb' + "'",strategy_term.sm_difficulty_low,
                                            strategy_term.sm_difficulty_high,strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            else:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                                           = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                                    (strategy_term.qb_id, "'" + 'fillb' + "'",
                                                                     strategy_term.sm_knowledge,
                                                                     strategy_term.sm_difficulty_low,
                                                                     strategy_term.sm_difficulty_high,
                                                                     strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            for question in result:
                                fillb_data = model.Fillb_model.getByPK(question.qt_id)
                                # 统计空数量
                                count = fillb_data.fb_pre_coding.count("&&&")
                                count = count / 2

                                eq_id_data = []
                                while count > 0:
                                    count = count - 1;
                                    # 添加exam_question
                                    exam_question = model.Exam_question_model()
                                    exam_question.information_in_id = information['in_id']
                                    exam_question.qt_id = question.qt_id
                                    exam_question.eq_qt_type = question.qt_type
                                    exam_question.eq_pre_score = strategy_term.sm_score
                                    exam_question.eq_answer = "答案"
                                    eq_id = exam_question.insertBackid()
                        if strategy_term.sm_type == 'coding':
                            if strategy_term.sm_knowledge==0:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and \
                                           qt_diffculty between %s and %s order by rand() limit %s' % \
                                           (strategy_term.qb_id, "'" + 'coding' + "'",strategy_term.sm_difficulty_low,
                                            strategy_term.sm_difficulty_high,strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            else:
                                result = model.Question_model.query('select * from question where qt_id \
                                          in (select question_qt_id from questions_bank_has_question where \
                                           questions_bank_qb_id = %s) and qt_type = %s and knowledge_kl_id \
                                           = %s and qt_diffculty between %s and %s order by rand() limit %s' % \
                                                                    (strategy_term.qb_id, "'" + 'coding' + "'",
                                                                     strategy_term.sm_knowledge,
                                                                     strategy_term.sm_difficulty_low,
                                                                     strategy_term.sm_difficulty_high,
                                                                     strategy_term.sm_number))
                                result = [model.Question_model(**item) for item in result]
                            for question in result:
                                # 添加exam_question
                                exam_question = model.Exam_question_model()
                                exam_question.information_in_id = information['in_id']
                                exam_question.qt_id = question.qt_id
                                exam_question.eq_qt_type = question.qt_type
                                exam_question.eq_pre_score = strategy_term.sm_score
                                exam_question.eq_answer = "答案"
                                eq_id = exam_question.insertBackid()
                    response = util.Response(status=util.Status.__success__,)
                    return util.objtojson(response)
                else:
                    print "ip_error"
                    response = util.Response(status=util.Status.__error__, message="ip_error")
                    return util.objtojson(response)
            elif information.in_state == '1':
                session.student_id = params.student_id
                session.ex_id = params.ex_id
                if datetime.datetime.now() >information.in_endtime:
                    response = util.Response(status=util.Status.__error__,message="exam is stop" )
                    return util.objtojson(response)
                if information.in_ip ==None:
                    information.in_ip = web.ctx.ip
                    information.update()
                if information.in_ip != web.ctx.ip:
                    print "ip 不统一"
                    response = util.Response(status=util.Status.__error__, message="必须使用同一台电脑登录")
                    return util.objtojson(response)
                response = util.Response(status=util.Status.__success__,)
                return util.objtojson(response)
            else:
                response = util.Response(status=util.Status.__error__, message="已结束考试")
                return util.objtojson(response)
                print "error"
        else:
            response = util.Response(status=util.Status.__error__, message="您不在该场考试")
            return util.objtojson(response)
            print "该场考试没有该学生"


class HandInExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        information = model.Information_model()
        session = web.ctx.session
        information_data = information.query('SELECT * FROM information WHERE \
                    student_st_id=%s and exam_ex_id=%s' % (session.student_id, session.ex_id))
        information = model.Information_model(**information_data[0])
        information.in_endtime = datetime.datetime.now()
        information.in_state = '2'
        information.in_temp_ip = None
        exam = model.Exam_model.getByPK(session.ex_id)
        if exam.ex_type=="0":
            util.SaveFillb(information.in_id)
            db.update('exam_question', where="information_in_id = %s" % (information.in_id), eq_get_score='-2', )
            # information.in_score = util.upInformationScore(1000,information.in_id)
            # while 1:
            #     exam_question = model.Exam_question_model.getByArgs(information_in_id=information.in_id)
            #     information.in_score = 0
            #     flag = 0
            #     for question in exam_question:
            #         if question.eq_get_score >= 0:
            #             information.in_score += question.eq_get_score
            #         else:
            #             flag = 1
            #             break
            #     if flag == 0:
            #         break
            #
            information.in_state = '0'
            information.update()
            response = util.Response(status=util.Status.__params_ok__,message=information.in_score )
            return util.objtojson(response)
        else:
            if exam.ex_auto =="1":
                util.SaveFillb(information.in_id)
                db.update('exam_question', where="information_in_id = %s" % (information.in_id), eq_get_score='-2', )
                thread.start_new(util.GetScore, (1,information.in_id))
            information.update()
            response = util.Response(status=util.Status.__success__, )
            return util.objtojson(response)
#
# class gettime:
#     def POST(self):
#         web.header("Access-Control-Allow-Origin", "*")
#         information = model.Information_model()
#         information_data = information.query('SELECT * FROM information WHERE \
#                     student_st_id=2014112200 and exam_ex_id=1')
#         information = model.Information_model(**information_data[0])
#         db.update('exam_question', where="information_in_id = %s"%(information.in_id), eq_get_score='-2', )
#         response = util.Response(status=util.Status.__success__,)
#         return util.objtojson(response)

class SelectExamQuestionById:
    def GET(self):
        session = web.ctx.session
        # print session.student_id
        print 'session.student_id ' + session.student_id
        return web.seeother('/static/exam/index.html',True)
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        information = model.Information_model()

        session = web.ctx.session
        information_data = information.query('SELECT * FROM information WHERE \
            student_st_id=%s and exam_ex_id=%s' % (session.student_id, session.ex_id))
        information = model.Information_model(**information_data[0])
        information.in_score = util.upInformationScore(information.in_id)
        information.update()
        exam_question = model.Exam_question_model.getByArgs(information_in_id=information.in_id)
        choice_question = []
        judge_question = []
        # filla是读程序写结果
        filla_question = []
        fillb_question = []
        coding_question = []
        for item in exam_question:
            if item.eq_get_score == -2:
                item.eq_get_score = u'未出分'
            if item.eq_qt_type == 'choice':
                question_data = model.Question_model.getByPK(item.qt_id)
                choice_data = model.Choice_model.getByPK(item.qt_id)
                item = dict(item, **choice_data)
                item = dict(item, **question_data)
                choice_question.append(item)
            elif item.eq_qt_type == 'judge':
                question_data = model.Question_model.getByPK(item.qt_id)
                judge_data = model.Judge_model.getByPK(item.qt_id)
                item = dict(item, **judge_data)
                item = dict(item, **question_data)
                judge_question.append(item)
            elif item.eq_qt_type == 'filla':
                question_data = model.Question_model.getByPK(item.qt_id)
                filla_data = model.Filla_model.getByPK(item.qt_id)
                item = dict(item, **filla_data)
                item = dict(item, **question_data)
                filla_question.append(item)
            elif item.eq_qt_type == 'coding':
                question_data = model.Question_model.getByPK(item.qt_id)
                coding_data = model.Coding_model.getByPK(item.qt_id)
                item = dict(item, **coding_data)
                item = dict(item, **question_data)
                coding_question.append(item)
        fillb_qt = model.Exam_question_model.query('select distinct(qt_id),\
                                                eq_pre_score from exam_question where information_in_id = %s \
                                                and eq_qt_type = %s' % (information.in_id, "'" + 'fillb' + "'"))
        for item in fillb_qt:
            question_data = model.Question_model.getByPK(item['qt_id'])
            fillb_data = model.Fillb_model.getByPK(item['qt_id'])
            eq_id_data = model.Exam_question_model.query('select eq_id,eq_answer,eq_get_score from \
                                                    exam_question where qt_id = %s and information_in_id = %s' \
                                                         % (item['qt_id'], information.in_id))
            eq_id_data = [model.Exam_question_model(**items) for items in eq_id_data]
            for question in eq_id_data:
                if question.eq_get_score <0:
                    question.eq_get_score = u'未出分'
            item = dict(item, **fillb_data)
            item = dict(item, **question_data)
            fillb = []
            fillb.append(item)
            fillb.append(eq_id_data)
            fillb_question.append(fillb)
        question_list = []
        question_list.append(choice_question)
        question_list.append(judge_question)
        question_list.append(filla_question)
        question_list.append(fillb_question)
        question_list.append(coding_question)
        student = model.Student_model.getByPK(session.student_id)
        exam = model.Exam_model.getByPK(session.ex_id)
        student['exam_name'] = exam.ex_name
        if information['in_score'] == -1:
            student['in_score'] = u'未出分,请稍后刷新该页面'
        else:
            student['in_score'] = information['in_score']
        question_list.append(student)
        time = information.in_endtime - datetime.datetime.now()
        count = time.seconds*1000
        response = util.Response(status=util.Status.__success__, body=question_list,message=count)
        return util.objtojson(response)

class SaveExam:
    def POST(self):
        web.header("Access-Control-Allow-Origin", "*")
        params = web.input()
        session = web.ctx.session
        exam_question = model.Exam_question_model(**params)
        exam_information = model.Information_model.query('select * from information\
         where student_st_id = %s and exam_ex_id = %s'%(session.student_id, session.ex_id))
        information = exam_information[0]
        if information.in_state !='1':
            print "已结束考试"
            response = util.Response(status=util.Status.__error__, message="已结束考试")
            return util.objtojson(response)
        if exam_question.update():
            time = information.in_endtime - datetime.datetime.now()
            count = time.seconds * 1000
            response = util.Response(status=util.Status.__success__,message=count)
            return util.objtojson(response)
        else:
            response = util.Response(status=util.Status.__error__, )
            return util.objtojson(response)



app = web.application(urls, globals())
render = web.template.render('template')
if __name__ == '__main__':
    if len(urls) & 1 == 1:
        print "urls error, the size of urls must be even."
    else:
        app.run()