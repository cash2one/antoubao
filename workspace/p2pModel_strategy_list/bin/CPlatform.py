#!/usr/bin/python
#encoding=utf-8

import CQualitative
import CQuantitative
import CScore

class Platform(object):
    def __init__(self):
        self.platform_name = ""
        self.platform_id = ""
        self.level = ""    
        self.qualitative = CQualitative()
        self.quantitative = CQuantitative()
        self.score = CScore()
