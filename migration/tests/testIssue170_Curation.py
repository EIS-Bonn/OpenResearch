'''
Created on 2021-04-15

@author: wf
'''
import unittest
from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.issue170_curation import CurationQualityChecker
from tests.corpus import Corpus
from collections import Counter

class TestIssue170(unittest.TestCase):
    '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/170
        
        Curation quality check
    '''
    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass


    def testCurationQualityCheck170(self):
        '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/170
        
        Curation quality check
        '''
        path=hf.getResourcePath() if hf.inPublicCI() else None
        userRating=CurationQualityChecker.loadUserRating(path)
        self.assertTrue("Wolfgang Fahl" in userRating)
        if self.debug:
            print(userRating)
        editingRecords= [
            {'lastEditor':'User:Wolfgang Fahl'}, 
            {'lastEditor':'User:194.95.114.12'},
            {'lastEditor':'User:John Doe'},
        ] 
        foundPains=[]
        for editingRecord in editingRecords:
            rating=CurationQualityChecker.getRating(editingRecord)
            if self.debug:
                print(f"{editingRecord}->{rating}")
            foundPains.append(rating.pain)
        #print(foundPains)
        self.assertEquals([3, 7, 7],foundPains)
        
    def testUserCount(self):
        # only needed to setup userrating yaml file
        eventCorpus=Corpus.getEventCorpus(debug=self.debug)
        userLookup=eventCorpus.eventList.getLookup("lastEditor",withDuplicates=True)
        if self.debug:
            print (f"{len(userLookup)} users")
        expected=1 if hf.inPublicCI() else 140
        self.assertTrue(len(userLookup)>expected)
        counter=Counter()
        for user in userLookup.keys():
            counter[user]+=len(userLookup[user])
        # hide personal data
        #print (counter.most_common(50))
            
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()