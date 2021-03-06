'''
Created on 21.07.2021

@author: wf
'''
from smw.pagefixer import EntityFixer, PageFixerManager
from openresearch.event import EventList, EventSeriesList

class ORFixer(EntityFixer):
    '''
    OpenResearch Fixer
    '''

    def __init__(self,pageFixerManager:PageFixerManager,debug=False):
        '''
        constructor
        '''
        super(ORFixer,self).__init__(pageFixerManager, debug)
        self.propertyLookups["Event"]=EventList.getPropertyLookup()
        self.propertyLookups["Event series"]=EventSeriesList.getPropertyLookup()
        