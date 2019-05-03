import time
import unittest
# from selenium.webdriver.common.keys import Keys
from xvfbwrapper import Xvfb
from common import SCZTest


# test COmanage
class SCZTestCOmanage(SCZTest):
    def test_comanage_login_testidp(self):
        d = self.driver

        # open COmanage and check that w eget the login page
        d.get(f'https://comanage.{self.base}/registry/')
        self.assertEqual("Home", self.driver.title)
        login_button = d.find_element_by_xpath('//*[@id="welcome-login"]')
        self.assertEqual("LOGIN", login_button.text)
        login_button.click()

        # select Test IdP
        self.scz_wayf_select_idp(self.test_idp_entityid, search_text='SCZ', idp_name=self.test_idp_name)

        time.sleep(1)

        # login
        self.scz_test_idp_login(self.test_idp_admin['user'], self.test_idp_admin['pass'])

        # check that we are in the correct COmanage
        self.assertEqual("COmanage Registry", d.find_element_by_xpath('//*[@id="collaborationTitle"]').text)
        self.assertEqual(f'https://comanage.{self.base}/registry/', d.current_url)
        # check that we have a "Platform" manu (i.e., that we are admin)
        self.assertEqual('Platform',
                         d.find_element_by_xpath('//li[@class="platformMenu"]//*/*[@class="menuTitle"]').text)

        self.test_result = 'pass'

    def test_comanage_login_student(self):
        d = self.driver

        # open COmanage and check that w eget the login page
        d.get(f'https://comanage.{self.base}/registry/')
        self.assertEqual("Home", self.driver.title)
        login_button = d.find_element_by_xpath('//*[@id="welcome-login"]')
        self.assertEqual("LOGIN", login_button.text)
        login_button.click()

        # select Test IdP
        self.scz_wayf_select_idp(self.test_idp_entityid, search_text='SCZ', idp_name=self.test_idp_name)

        time.sleep(1)

        # login
        self.scz_test_idp_login(self.test_idp_student['user'], self.test_idp_student['pass'])

        # check that we are in the correct COmanage
        self.assertEqual("COmanage Registry", d.find_element_by_xpath('//*[@id="collaborationTitle"]').text)
        self.assertEqual(f'https://comanage.{self.base}/registry/', d.current_url)
        # check that we don't have access and that our eppn is correct
        self.assertIn('The identifier "eppn_student@surfnet.nl|eptid_student@surfnet.nl" is not registered.',
                       d.find_element_by_xpath('//div[@class="co-info-topbox"]').text)

        self.test_result = 'pass'

    def test_pyff_edugain(self):
        d = self.driver

        # open mdq
        d.get(f'https://mdq.{self.base}/')
        r_and_s = d.find_elements_by_xpath('//*[@id="entity-category"]//*/a[@href="/entity-category/http%3A%2F%2Fid.incommon.org%2Fcategory%2Fregistered-by-incommon.html"]')
        self.assertNotEqual(len(r_and_s), 0)




if __name__ == '__main__':
    display = Xvfb(width=1280, height=740, colordepth=16)
    # display.start()
    unittest.main()  # display.stop()
