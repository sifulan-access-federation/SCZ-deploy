import unittest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.common.keys import Keys
from xvfbwrapper import Xvfb
from time import sleep


class Selenium(unittest.TestCase):
    def __init__(self, method_name='runTest'):
        self.base = 'test.scz.lab.surf.nl'
        self.test_idp_entityid = "https://idp-test.test.scz.lab.surf.nl/saml/saml2/idp/metadata.php"
        self.test_idp_name = "SCZ Test IdP"
        self.test_idp_admin = {"user": "baas", "pass": "baas"}
        super(Selenium, self).__init__(method_name)

    def setUp(self):
        self.test_result = None

        self.driver = webdriver.Firefox()
        self.driver.delete_all_cookies()
        self.driver.implicitly_wait(20)

    def tearDown(self):
        if self.driver.session_id:
            self.driver.quit()
        pass

    # shortcut to select the idp with the specified entityid in the pyFf decivery screen
    def _wayf_select_idp(self, entityid, search_text=None, idp_name = None):
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
        idp_selector = d.find_element_by_xpath(
            f'//*[@id="ds-search-list"]/div[@data-href="{entityid}"]//*/h5')

        # extra check for the correct idp name, if requested
        if idp_name is not None:
            self.assertEqual(idp_name, idp_selector.text)

        idp_selector.click()

    def _test_idp_login(self, username, password):
        d = self.driver

        self.assertEqual("Enter your username and password", self.driver.title)
        d.find_element_by_id('username').send_keys(username)
        d.find_element_by_id('password').send_keys(password)
        d.find_element_by_xpath('//*[@id="submit"]//*/button').click()

    def test_comanage_login_testidp(self):
        d = self.driver

        d.get(f'https://comanage.{self.base}/registry/')
        self.assertEqual("Home", self.driver.title)
        login_button = d.find_element_by_xpath('//*[@id="welcome-login"]')
        self.assertEqual("LOGIN", login_button.text)
        login_button.click()

        self._wayf_select_idp(self.test_idp_entityid, search_text='SCZ', idp_name=self.test_idp_name)

        self._test_idp_login(self.test_idp_admin['user'], self.test_idp_admin['pass'])

        self.assertEqual("COmanage Registry", d.find_element_by_xpath('//*[@id="collaborationTitle"]').text)
        self.assertEqual(f'https://comanage.{self.base}/registry/', d.current_url)
        self.assertEqual('Platform',
            d.find_element_by_xpath('//li[@class="platformMenu"]//*/*[@class="menuTitle"]').text)

        sleep(2)
        self.test_result = 'pass'


if __name__ == '__main__':
    display = Xvfb(width=1280, height=740, colordepth=16)
    #display.start()
    unittest.main()
    #display.stop()
