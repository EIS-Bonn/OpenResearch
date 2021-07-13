'''
Created on 2021-07-13

@author: wf
'''
import unittest
import os
from ormigrate.fixer import PageFixer
from ormigrate.issue150_nullvalue import NullValueFixer

class TestNullValueFixer(unittest.TestCase):
    '''
    Test the fixer for Fixer for https://github.com/SmartDataAnalytics/OpenResearch/issues/150
    '''

    def setUp(self):
        self.debug=True
        pass

    def tearDown(self):
        pass

    def testNullValueFixer(self):
        '''
        test fixing https://confident.dbis.rwth-aachen.de/or/index.php?title=ECIR
        '''
        # TODO - create a helper function to create arguments for command line
        pageTitles=["ECIR 2019","ECIR 2018","ECIR 2017","ECIR 2009"]
        wikiId="orclone"
        args=["--pages"]
        home = os.path.expanduser("~")
        for pageTitle in pageTitles:
            args.append(pageTitle)
        args.append("--source")
        args.append(wikiId)
        args.append("--wikiTextPath")
        wikiTextPath=f"{home}/.or/wikibackup/{wikiId}"
        args.append(wikiTextPath)
        if self.debug:
            print(args)
        ratings,errors=PageFixer.cmdLine([NullValueFixer],args)   
        if len(errors)>0:
            print(errors) 
        self.assertEqual(0,len(errors))
        if self.debug:
            for i,pageTitle in enumerate(ratings):
                print(f"{i+1}:{pageTitle}->{ratings[pageTitle]}")
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()