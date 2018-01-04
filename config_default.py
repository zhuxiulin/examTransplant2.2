#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Default configurations.
'''

configs = {
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'admin',
        'password': 'EXAMhost#6636',
        'database': 'examdb'
    },
    'session': {
        'secret': 'AwEsOmE'
    },     
}
question_source=u'../examTransplant2.2/source/question'
student_source =u'../examTransplant2.2/source/excel'
remind_source = u'../examTransplant2.2/source'
exampage_source =u'../examTransplant2.2/source/exampage'
server_num=2
