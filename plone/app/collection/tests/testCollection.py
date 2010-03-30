import unittest

from plone.app.collection.tests.base import CollectionTestCase, CollectionFunctionalTestCase
from Products.Five.testbrowser import Browser
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest 


class TestCollection(CollectionFunctionalTestCase):
    
    def afterSetUp(self):
        self.loginAsPortalOwner()
        collection_id = self.portal.invokeFactory("Collection", "NewCollection")
        self.collection = self.portal[collection_id]
        self.portal.portal_workflow.doActionFor(self.collection, 'publish')
    
        testpage_id = self.portal.invokeFactory("Document",'collectionstestpage', title="Collectionstestpage")
        self.portal.portal_workflow.doActionFor(self.portal['collectionstestpage'], 'publish')
        
    def test_viewingCollection(self):
        query = [{
            'i': 'Title',
            'o': 'plone.app.collection.operation.string.is',
            'v': 'Collectionstestpage',
        }]
        self.collection.setQuery(query)
        self.assertEqual(self.collection.getQuery()[0].Title(), "Collectionstestpage")
        browser = Browser()
        browser.open(self.collection.absolute_url())
        self.failUnless("Collectionstestpage" in browser.contents)

class TestQuerybuilder(CollectionTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        testpage_id = self.portal.invokeFactory("Document",'collectionstestpage', title="Collectionstestpage")
        self.portal.portal_workflow.doActionFor(self.portal['collectionstestpage'], 'publish')
        self.request = TestRequest()      
        self.querybuilder = getMultiAdapter((self.portal, self.request), name='querybuilderresults')
        self.query = [{
            'i': 'Title',
            'o': 'plone.app.collection.operation.string.is',
            'v': 'Collectionstestpage',
        }]
        
    def testQueryBuilderQuery(self):
        results = self.querybuilder(query=self.query)
        self.assertEqual(results[0].Title(), "Collectionstestpage")

    def testQueryBuilderNumberOfResults(self):
        results = self.querybuilder.number_of_results(self.query)
        numeric = int(results.split(' ')[0])
        self.assertEqual(numeric,1)

    def testQueryBuilderNumberOfResults2(self):
        length_of_results = self.folder.restrictedTraverse('@@querybuildernumberofresults').browserDefault(None)[0](self.query)
        # apparently brower travelsal is different from the traversal we get from restrictedTraverse. This did hurt a bit.
        numeric = int(length_of_results.split(' ')[0])
        self.assertEqual(numeric,1)
        
    def testQueryBuilderHTML(self):
        self.failUnless('Collectionstestpage' in self.querybuilder.html_results(self.query))

    def testGettingConfiguration(self):
        self.folder.restrictedTraverse('@@querybuildernumberofresults')(self.query)


class TestConfigurationFetcher(CollectionTestCase):

    def testGettingJSONConfiguration(self):
        configuration = self.folder.restrictedTraverse('@@querybuilderjsonconfig')()

        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCollection))
    suite.addTest(unittest.makeSuite(TestQuerybuilder))
    suite.addTest(unittest.makeSuite(TestConfigurationFetcher))
    return suite
