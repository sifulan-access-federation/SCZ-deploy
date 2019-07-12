import time
import unittest

from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions

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
        r_and_s = d.find_elements_by_xpath('//*[@id="entity-category"]//*/a[@href="/entity-category/'
                                           'http%3A%2F%2Fid.incommon.org%2Fcategory%2Fregistered-by-incommon.html"]')
        self.assertNotEqual(len(r_and_s), 0)

    def scz_testsp_SAML(self, proxy_type):
        d = self.driver

        # open test client
        d.get(f'https://sp-test.{self.base}/saml/module.php/core/authenticate.php?as=default-sp')
        self.assertEqual("Select your identity provider", d.title)

        idp_list = d.find_element_by_name('idpentityid')
        Select(idp_list).select_by_visible_text(proxy_type)
        idp_list.submit()

        # select Test IdP
        if proxy_type == "SCZ Test Normal Proxy":
            self.scz_wayf_select_idp(self.test_idp_entityid, search_text='SCZ', idp_name=self.test_idp_name)

        # login
        self.scz_test_idp_login(self.test_idp_student['user'], self.test_idp_student['pass'])

        if d.current_url.startswith(f'https://cm.{self.base}'):
            d.find_element_by_id('submit_ok').click()

        self.wait.until(expected_conditions.url_contains('https://sp-test'))
        self.wait.until(expected_conditions.title_contains('SP Demo'))
        self.assertEqual("SAML 2.0 SP Demo Example", d.title)
        attribute_cells = d.find_elements_by_xpath('//*[@id="table_with_attributes"][1]//tr/td[@class="attrname"]')
        attributes = [x.text for x in attribute_cells]
        self.assertEqual(2, len(attributes))
        self.assertIn('idpcountry', attributes)
        self.assertIn('idpname', attributes)

    def test_testsp_SAML_proxy(self):
        return self.scz_testsp_SAML('SCZ Test Normal Proxy')

    def test_testsp_SAML_mirror_mirror(self):
        return self.scz_testsp_SAML('SCZ Test Mirrored Proxy Mirrored SP')

    def test_testsp_SAML_mirror_normal(self):
        return self.scz_testsp_SAML('SCZ Test Mirrored Proxy Normal SP')

    def test_testsp_SURFconext_diy(self):
        d = self.driver

        # open test client
        d.get(f'https://sp-test.{self.base}/saml/module.php/core/authenticate.php?as=default-sp')
        self.assertEqual("Select your identity provider", d.title)

        idp_list = d.find_element_by_name('idpentityid')
        Select(idp_list).select_by_visible_text('SCZ Test Normal Proxy')
        idp_list.submit()

        # select Test IdP
        self.scz_wayf_select_idp(self.sc_diyidp_entityid, search_text='SURFconext', idp_name=self.sc_diyidp_name)

        # login
        self.scz_sctest_idp_login('student5')

        # wait for redirects to settle
        self.wait.until(expected_conditions.url_matches(f'^https://(sp-test|cm)\\.{self.base}.*'))

        # handle consent
        if d.current_url.startswith(f'https://cm.{self.base}'):
            d.find_element_by_id('submit_ok').click()

        self.wait.until(expected_conditions.title_contains('SP Demo'))
        self.assertEqual("SAML 2.0 SP Demo Example", d.title)
        attr_names = [a.text for a in
                      d.find_elements_by_xpath('//*[@id="table_with_attributes"][1]//tr/td[@class="attrname"]')]

        for a in ['givenName', 'sn', 'displayName', 'cn', 'mail', 'eduPersonAffiliation', 'isMemberOf']:
            self.assertIn(f'urn:mace:dir:attribute-def:{a}', attr_names)

    def test_testsp_OIDC(self):
        d = self.driver

        # open test client
        d.get(f'https://oidc-test.{self.base}/oidc')

        # select test IdP
        self.scz_wayf_select_idp(self.test_idp_entityid, search_text='SCZ', idp_name=self.test_idp_name)

        # login
        self.scz_test_idp_login(self.test_idp_student['user'], self.test_idp_student['pass'])

        if d.current_url.startswith(f'https://cm.{self.base}'):
            d.find_element_by_id('submit_ok').click()

        self.wait.until(expected_conditions.url_contains('https://oidc-test'))
        self.assertEqual("OIDC RP Test", d.find_element_by_tag_name('h1').text)
        attributes = [p.text for p in d.find_elements_by_xpath('//p')]
        self.assertEqual(11, len(attributes))


if __name__ == '__main__':
    display = Xvfb(width=1280, height=740, colordepth=16)
    # display.start()
    unittest.main()  # display.stop()
