'''
Created on 2021-04-15

@author: wf
'''
from smw.pagefixer import PageFixer,PageFixerManager
from smw.rating import Rating,RatingType
from openresearch.openresearch import OpenResearch
import yaml
import os
from smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer


class CurationQualityChecker(ORFixer):
    '''
    see purpose and issue
    '''
    purpose="Curation quality check"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/170"
    userrating={}
    
    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(CurationQualityChecker, self).__init__(pageFixerManager)
    
    @classmethod
    def loadUserRating(cls,path=None):
        '''
        load the user rating from the given path
        '''
        if len(CurationQualityChecker.userrating)==0:
            if path is None:
                path=OpenResearch.getCachePath()
            yamlPath=f"{path}/userrating.yaml"
            if os.path.isfile(yamlPath):
                with open(yamlPath, 'r') as stream:
                    CurationQualityChecker.userrating = yaml.safe_load(stream)
        return CurationQualityChecker.userrating
    
    @classmethod
    def getRating(cls,entityRecord):
        userRating=cls.loadUserRating()
        if 'lastEditor' in entityRecord:
            userName=entityRecord['lastEditor'].replace('User:','')
            if userName in userRating:
                painRecord=userRating[userName]
                return Rating(painRecord['pain'],RatingType.ok,painRecord['hint'])
            else:
                return Rating(7,RatingType.invalid,'last edited by unrated curator')
        else:   
            return Rating(10,RatingType.missing,'bug: lastEditor not set')
        
if __name__ == "__main__":
    PageFixerManager.runCmdLine([CurationQualityChecker])