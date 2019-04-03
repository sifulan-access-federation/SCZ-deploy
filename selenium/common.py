import unittest
from time import sleep
import os
import datetime

from selenium import webdriver
from selenium.webdriver import ActionChains


# generic class for SCZ tests
# includes selenium setup and generic helper methods for common functionality
class SCZTest(unittest.TestCase):
    def __init__(self, method_name='runTest'):
        self.base = 'test.scz.lab.surf.nl'
        self.test_idp_entityid = f'https://idp-test.{self.base}/saml/saml2/idp/metadata.php'
        self.test_idp_name = "SCZ Test IdP"
        self.test_idp_admin = {"user": "baas", "pass": "baas"}
        date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        self.log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     "..", "logs", f"selenium_firefox.{date_str}.log")
        super(SCZTest, self).__init__(method_name)

    def setUp(self):
        self.driver = webdriver.Firefox(service_log_path=self.log_file)
        self.driver.delete_all_cookies()
        self.driver.implicitly_wait(20)

    def tearDown(self):
        if self.driver.session_id:
            self.driver.quit()

    # shortcut method to select the idp with the specified entityid in the pyFF decovery screen
    def scz_wayf_select_idp(self, entityid, search_text=None, idp_name=None):
        d = self.driver

        # if no search text was specified, we simply search for the entityid
        if search_text is None:
            search_text = entityid

        # check that we are at the correct location
        self.assertTrue(d.current_url.startswith(f'https://mdq.{self.base}/'))

        # enter search text in text box
        idp_searchbox = d.find_element_by_xpath('//*[@id="searchinput"]')
        ActionChains(d).move_to_element(idp_searchbox).send_keys(search_text).perform()
        sleep(1.0)

        # find correct idp item
        idp_selector = d.find_element_by_xpath(f'//*[@id="ds-search-list"]/div[@data-href="{entityid}"]//*/h5')

        # extra check for the correct idp name, if requested
        if idp_name is not None:
            self.assertEqual(idp_name, idp_selector.text)

        idp_selector.click()

    # shortcut method to login to the Test IdP with the provided credentials
    def scz_test_idp_login(self, username, password):
        d = self.driver

        self.assertEqual("Enter your username and password", self.driver.title)
        d.find_element_by_id('username').send_keys(username)
        d.find_element_by_id('password').send_keys(password)
        d.find_element_by_xpath('//*[@id="submit"]//*/button').click()
