'''
Created on 2021-04-02

@author: wf
'''
import unittest
import io
from os import path
from ormigrate.issue152 import AcceptanceRateFixer
from ormigrate.issue119_Ordinals import OrdinalFixer
from ormigrate.issue71 import DateFixer
from ormigrate.issue163 import SeriesFixer
from ormigrate.issue166 import WikiCFPIDFixer

from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.fixer import PageFixer
from openresearch.event import Event
from lodstorage.jsonable import Types

class TestDataFixes(unittest.TestCase):

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass

    def testDateParser(self):
        '''
        test the date parser used to convert dates in issue 71
        '''
        sampledates=['2020-02-20','2020/02/20','2020.02.20','20/02/2020','02/20/2020','20.02.2020','02.20.2020','20 Feb, 2020','2020, Feb 20','2020 20 Feb','2020 Feb 20']
        for date in sampledates:
            self.assertEqual('2020/02/20',hf.parseDate(date))

    '''
     @TODO       
    # def testDirectoryExists(self):
    #     ensureDirectoryExists('./test')
    #     self.assertTrue(os.path.exists('./test'))
    #     os.remove('./test')
    '''
    def testNameValue(self):
        '''
        test the name value helper function
        '''
        nameValues=["|a=1","|b= a=c ","|w|b",'|a=']
        pageFixer=PageFixer()
        for i,nameValue in enumerate(nameValues):
            name,value=pageFixer.getNameValue(nameValue)
            if self.debug:
                print("%d: %s=%s" % (i,name,value))
            if i==0: self.assertEqual(name,"a") 
            if i==1: self.assertEqual(value,"a=c")
            if i==2: self.assertIsNone(value)
            if i==3: self.assertIsNone(value)
        

    def testGetAllPagesFromFile(self):
        '''
        test utility function to get pageTitles from a file e.g. stdin
        '''
        pageFixer=PageFixer()
        # we'd love to test form a string
        # see https://stackoverflow.com/a/141451/1497139
        pageTitles="""Concept:Topic
Help:Topic"""
        fstdin = io.StringIO(pageTitles)
        pageTitleList=pageFixer.getAllPagesFromFile(fstdin)
        self.assertEqual(2,len(pageTitleList))

    def testFixedPath(self):
        fixer = DateFixer(debug=self.debug)
        dirname= 'Fixed'
        fixedPath = fixer.getFixedPagePath('/asd/asd/asd/test.wiki',dirname)
        self.assertTrue(fixedPath == '%s/wikibackup/%s/%s' % (path.expanduser("~"), dirname, 'test.wiki'))

    def testIssue152(self):
        '''
            test for fixing Acceptance Rate Not calculated
            https://github.com/SmartDataAnalytics/OpenResearch/issues/152
        '''
        eventRecords= [{'submittedPapers':'test', 'acceptedPapers':'test'},
                       {'submittedPapers': None, 'acceptedPapers':None},
                       {'submittedPapers':'test', 'acceptedPapers':None},
                       {'submittedPapers':None, 'acceptedPapers':'test'}]
        painRatings=[]
        fixer=AcceptanceRateFixer(debug=self.debug)

        for event in eventRecords:
            painRating =fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating)
        self.assertEqual(painRatings,[1,2,3,4])
        pages=fixer.getAllPages()
        if self.debug:
            print("Number of pages: ", len(pages))
        expectedPages=0 if hf.inPublicCI() else 8000
        self.assertTrue(len(pages)>=expectedPages)
        events=list(fixer.getAllPageTitles4Topic("Event"))
        expectedEvents=0 if hf.inPublicCI() else 5500
        if self.debug:
            print("Number of events: ", len(events))
        self.assertTrue(len(events)>=expectedEvents)
        fixer.checkAllFiles(fixer.check)
        if self.debug:
            print(fixer.result())
            print(expectedEvents)
        self.assertTrue(fixer.nosub>=0 if hf.inPublicCI() else 50)
        self.assertTrue(fixer.nosub>=0 if hf.inPublicCI() else 50)

    def testDictionaryLoad(self):
        """
        test for loading the lookup Dictionary
        """
        lookup_dict=hf.loadDictionary
        self.assertIsNotNone(lookup_dict)

    def testIssue119(self):
        '''
            test for fixing Ordinals not a number
            https://github.com/SmartDataAnalytics/OpenResearch/issues/119
        '''
        eventRecords= [{'Ordinal':2},
                       {'Ordinal':None},
                       {'Ordinal':'2nd'},
                       {'Ordinal':'test'}]
        painRatings = []
        fixer=OrdinalFixer(debug=self.debug)
        for event in eventRecords:
            painRating = fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(painRatings,[1,4,5,7])
        types = Types("Event")
        samples = Event.getSampleWikiSon()
        lookup_dict = hf.loadDictionary()
        fixed=fixer.convert_ordinal_to_cardinal('sample',samples[0],lookup_dict)
        fixed_dic=hf.wikiSontoLOD(fixed)
        types.getTypes("events", fixed_dic, 1)
        self.assertTrue(types.typeMap['events']['Ordinal'] == 'int')

    def testIssue71(self):
        '''
            test for fixing invalid dates
            https://github.com/SmartDataAnalytics/OpenResearch/issues/71
        '''
        eventRecords = [{'startDate': '20 Feb, 2020', 'endDate': '20 Feb, 2020'},
                        {'startDate': None, 'endDate': None},
                        {'startDate': '20 Feb, 2020', 'endDate': None},
                        {'startDate': None, 'endDate': '20 Feb, 2020'},
                        {'startDate': '20 Feb, 2020', 'endDate': 'test'},
                        {'startDate': 'test', 'endDate': '20 Feb, 2020'},
                        {'startDate': 'test', 'endDate': 'test'}]
        painRatings=[]
        fixer=DateFixer(debug=self.debug)
        for event in eventRecords:
            painRating = fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating)
        self.assertEqual(painRatings,[1,2,3,4,5,6,7])

        types = Types("Event")
        samples = Event.getSampleWikiSon()
        fixedDates=fixer.getFixedDate('sample',samples[0])
        fixedDeadlines=fixer.getFixedDate('sample',fixedDates,'deadline')
        fixed_dic=hf.wikiSontoLOD(fixedDeadlines)
        self.assertTrue(fixed_dic[0]['Start date'] == '2020/09/27')
        self.assertTrue(fixed_dic[0]['Paper deadline'] == '2020/05/28')

    def testIssue163(self):
        '''
        Series Fixer
        '''
        #self.debug=True
        fixer=SeriesFixer(debug=self.debug)
        askExtra="" if hf.inPublicCI() else "[[Creation date::>2018]][[Creation date::<2020]]"
        count=fixer.checkAll(askExtra)
        # TODO: we do not test the count here  - later we want it to be zero

    def testdictToWikison(self):
        """
        Test the helper function to create wikison from a given dict
        """
        samples= Event.getSamples()
        for sample in samples:
            dic=hf.dicttoWikiSon(sample)
            self.assertEqual(type(dic),str)
            self.assertIsNotNone(dic)
            self.assertIn('acronym', dic)

    def testWikisontoDict(self):
        """
        Test the helper function to create wikison from a given dict
        """
        samples= Event.getSampleWikiSon()
        for sample in samples:
            dic=hf.wikiSontoLOD(sample)
            self.assertEqual(type(dic[0]),dict)
            self.assertIsNotNone(dic[0])
            self.assertIn('Acronym', dic[0])


    def testIssue166(self):
        """
        Tests the issue 166 for addition of WikiCFP-ID to applicable pages
        """
        if hf.inPublicCI():
            # TODO: Need the Events DB in project to run the test.
            pass
        else:
            fixer= WikiCFPIDFixer()
            samples = Event.getSampleWikiSon()
            wikicfpid= fixer.getPageWithWikicfpid('test',samples[1])
            self.assertIsNotNone(wikicfpid)
            self.assertEqual(wikicfpid,'3845')
            fixedPage= fixer.fixPageWithDplp('test',samples[1],wikicfpid)
            if self.debug:
                print(fixedPage)
            fixedDict=hf.wikiSontoLOD(fixedPage)[0]
            self.assertIsNotNone(fixedDict['WikiCFP-ID'])
            self.assertEqual(fixedDict['WikiCFP-ID'],3845)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()