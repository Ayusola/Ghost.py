# -*- coding: utf-8 -*-
import thread
import unittest
from casper import Casper
from app import app

PORT = 5000

thread.start_new_thread(app.run, (), {'port': PORT})
base_url = 'http://localhost:%s/' % PORT


class CapserTest(unittest.TestCase):

    casper = Casper()

    def test_open(self):
        ressources = self.casper.open(base_url)
        self.assertEqual(ressources[0].url, base_url)
        self.assertTrue("Test page" in self.casper.content)

    def test_http_status(self):
        ressources = self.casper.open("%sredirect-me" % base_url)
        self.assertEqual(ressources[0].http_status, 302)
        ressources = self.casper.open("%s404" % base_url)
        self.assertEqual(ressources[0].http_status, 404)

    def test_evaluate(self):
        self.casper.open(base_url)
        self.assertEqual(self.casper.evaluate("x='casper'; x;")[0], 'casper')

    def test_external_api(self):
        ressources = self.casper.open("%smootools" % base_url)
        self.assertEqual(len(ressources), 2)
        self.assertEqual(self.casper.evaluate("document.id('list')")[0].type(),
            8)
        self.assertEqual(self.casper.evaluate("document.id('list')")[0],
            self.casper.evaluate("document.getElementById('list')")[0])

    def test_wait_for_selector(self):
        ressources = self.casper.open("%smootools" % base_url)
        success, ressources = self.casper.click("#button")
        # This is loaded via XHR :)
        success, ressources = self.casper\
            .wait_for_selector("#list li:nth-child(2)")
        self.assertEqual(ressources[0].url, "%sitems.json" % base_url)

    def test_wait_for_text(self):
        ressources = self.casper.open("%smootools" % base_url)
        self.casper.click("#button")
        # This is loaded via XHR :)
        success, ressources = self.casper.wait_for_text("second item")
        self.assertEqual(ressources[0].url, "%sitems.json" % base_url)

    def test_fill(self):
        self.casper.open("%scontact" % base_url)
        values = {
            'subject': 'Here is the subject',
            'email': 'my@awesome.email',
            'message': 'Here is my message.',
            'important': True
        }
        self.casper.fill('#contact-form', values)
        for field in ['subject', 'email', 'message']:
            value, resssources = self.casper\
                .evaluate('document.getElementById("%s").value' % field)
            self.assertEqual(value.toString(), values[field])
        value, ressources = self.casper.evaluate(
            'document.getElementById("important").checked')
        self.assertEqual(value, True)

if __name__ == '__main__':
    unittest.main()