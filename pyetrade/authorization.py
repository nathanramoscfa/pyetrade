"""Authorization - ETrade Authorization API Calls"""

import re
import logging
from requests_oauthlib import OAuth1Session
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, InvalidSessionIdException

# Set up logging
LOGGER = logging.getLogger(__name__)


class ETradeOAuth(object):
    """:description: Performs authorization for OAuth 1.0a

       :param consumer_key: Client key provided by Etrade
       :type consumer_key: str, required
       :param consumer_secret: Client secret provided by Etrade
       :type consumer_secret: str, required
       :param web_username: Client web username for Etrade
       :type web_username: str, required
       :param web_password: Client web password for Etrade
       :type web_password: str, required
       :param etrade_cookie: Client cookie. Must request from E-Trade.
       :type etrade_cookie: dict, required
       :param callback_url: Callback URL passed to OAuth mod, defaults to "oob"
       :type callback_url: str, optional
       :EtradeRef: https://apisb.etrade.com/docs/api/authorization/request_token.html

    """

    def __init__(self, consumer_key, consumer_secret, web_username, web_password, etrade_cookie, callback_url="oob"):

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.web_username = web_username
        self.web_password = web_password
        self.etrade_cookie = etrade_cookie
        self.base_url_prod = r"https://api.etrade.com"
        self.base_url_dev = r"https://apisb.etrade.com"
        self.req_token_url = r"https://api.etrade.com/oauth/request_token"
        self.auth_token_url = r"https://us.etrade.com/e/t/etws/authorize"
        self.access_token_url = r"https://api.etrade.com/oauth/access_token"
        self.callback_url = callback_url
        self.access_token = None
        self.resource_owner_key = None
        self.session = None
        self.verifier_url = None

    def get_request_token(self):
        """:description: Obtains the token URL from Etrade.

           :return: Formatted Authorization URL (Access this to obtain taken)
           :rtype: str
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/request_token.html

        """

        # Set up session
        self.session = OAuth1Session(
            self.consumer_key,
            self.consumer_secret,
            callback_uri=self.callback_url,
            signature_type="AUTH_HEADER",
        )
        # get request token
        self.session.fetch_request_token(self.req_token_url)
        # get authorization url
        # etrade format: url?key&token
        authorization_url = self.session.authorization_url(self.auth_token_url)
        akey = self.session.parse_authorization_response(authorization_url)
        # store oauth_token
        self.resource_owner_key = akey["oauth_token"]
        formated_auth_url = "%s?key=%s&token=%s" % (
            self.auth_token_url,
            self.consumer_key,
            akey["oauth_token"],
        )
        self.verifier_url = formated_auth_url
        LOGGER.debug(formated_auth_url)

        return formated_auth_url

    def get_verification_code(self, headless=False):
        """:description: Obtains verification code for signing in to E-Trade.

           :param headless: Option to run browser in headless mode, defaults to False
           :type headless: bool, optional
           :return: Verification code (Used for two-factor authentication)
           :rtype: str

        """
        formated_auth_url = self.get_request_token()
        driver = self.initialize_driver(headless)

        driver.get(formated_auth_url)
        driver.add_cookie(self.etrade_cookie)
        self.login_to_site(driver)

        verifier = self.get_verifier(driver)
        return verifier

    @staticmethod
    def initialize_driver(headless):
        """:description: Initialize the web driver with specified options.

           :param headless: Option to run browser in headless mode, defaults to False
           :type headless: bool, optional
           :return: Selenium web driver
           :rtype: selenium.webdriver.chrome.webdriver.WebDriver

        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")

        options.add_argument("--log-level=3")  # Fatal
        options.add_argument("--disable-logging")

        try:
            return webdriver.Chrome(ChromeDriverManager().install(), options=options)
        except SessionNotCreatedException as e:
            required_version = re.search(r"only supports Chrome version ([\d.]+)", str(e)).group(1)
            print(
                f"SessionNotCreatedException occurred. Attempting to download ChromeDriver for version {required_version}.")
            return webdriver.Chrome(ChromeDriverManager(driver_version=required_version).install(), options=options)

    def login_to_site(self, driver):
        """:description: Perform login operation using the driver.

           :param driver: Selenium driver object
           :type driver: selenium.webdriver.chrome.webdriver.WebDriver
           :return: None
           :rtype: None

        """
        user_id = driver.find_element(By.CSS_SELECTOR, '#USER')
        password = driver.find_element(By.CSS_SELECTOR, '#password')
        logon_button = driver.find_element(By.CSS_SELECTOR, '#mfaLogonButton')

        user_id.send_keys(self.web_username)
        password.send_keys(self.web_password)
        logon_button.click()

        driver.implicitly_wait(5)

        try:
            accept = driver.find_element(By.NAME, "submit")
            accept.click()
        except NoSuchElementException:
            pass

    def get_verifier(self, driver):
        """:description: Obtain the verification code from the site.

           :param driver: Selenium driver object
           :type driver: selenium.webdriver.chrome.webdriver.WebDriver
           :return: Verification code
           :rtype: str

        """
        try:
            verifier_element = driver.find_element(By.XPATH, "//div[@style='text-align:center']/input[1]")
            return verifier_element.get_attribute('value') if verifier_element else None
        except InvalidSessionIdException:
            pass
        except NoSuchElementException:
            self.handle_no_element_exception(driver)

    def handle_no_element_exception(self, driver):
        """:description: Handle case when a necessary element is not found.

           :param driver: Selenium driver object
           :type driver: selenium.webdriver.chrome.webdriver.WebDriver
           :return: None
           :rtype: None

        """
        driver.find_element(By.CSS_SELECTOR, "#sendOTPCodeBtn").click()
        verifier = input("Check your mobile phone. Enter the verification code: ")
        self.enter_verification_code(driver, verifier)
        try:
            accept = driver.find_element(By.NAME, "submit")
            accept.click()
        except NoSuchElementException:
            pass

    @staticmethod
    def enter_verification_code(driver, verifier):
        """:description: Enters verification code for signing in to E-Trade.

           :param driver: Selenium driver object
           :type driver: selenium.webdriver.chrome.webdriver.WebDriver
           :param verifier: Verification code from E-Trade
           :type verifier: str, required
           :return: None
           :rtype: None

        """
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#verificationCode"))).send_keys(verifier)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "fieldset > div:nth-child(1) > label"))).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#application > div > div.row > div > div:nth-child(3) > "
                                                             "div:nth-child(4) > button"))).click()

    def get_access_token(self, verifier):
        """:description: Obtains access token. Requires token URL from :class:`get_request_token`

           :param verifier: OAuth Verification Code from Etrade
           :type verifier: str, required
           :return: OAuth access tokens
           :rtype: dict
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/get_access_token.html

        """
        # Set verifier
        self.session._client.client.verifier = verifier
        # Get access token
        self.access_token = self.session.fetch_access_token(self.access_token_url)
        LOGGER.debug(self.access_token)

        return self.access_token


class ETradeAccessManager(object):
    """:description: Renews and revokes ETrade OAuth access tokens

       :param client_key: Client key provided by Etrade
       :type client_key: str, required
       :param client_secret: Client secret provided by Etrade
       :type client_secret: str, required
       :param resource_owner_key: Resource key from :class:`ETradeOAuth`
       :type resource_owner_key: str, required
       :param resource_owner_secret: Resource secret from :class:`ETradeOAuth`
       :type resource_owner_secret: str, required
       :EtradeRef: https://apisb.etrade.com/docs/api/authorization/renew_access_token.html

    """

    def __init__(
            self, client_key, client_secret, resource_owner_key, resource_owner_secret
    ):
        self.client_key = client_key
        self.client_secret = client_secret
        self.resource_owner_key = resource_owner_key
        self.resource_owner_secret = resource_owner_secret
        self.renew_access_token_url = r"https://api.etrade.com/oauth/renew_access_token"
        self.revoke_access_token_url = r"https://api.etrade.com/oauth/revoke_access_token"
        self.session = OAuth1Session(
            self.client_key,
            self.client_secret,
            self.resource_owner_key,
            self.resource_owner_secret,
            signature_type="AUTH_HEADER",
        )

    def renew_access_token(self):
        """:description: Renews access tokens obtained from :class:`ETradeOAuth`

           :return: Success or failure
           :rtype: bool (True or False)
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/renew_access_token.html

        """
        resp = self.session.get(self.renew_access_token_url)
        LOGGER.debug(resp.text)
        resp.raise_for_status()

        return True

    def revoke_access_token(self):
        """:description: Revokes access tokens obtained from :class:`ETradeOAuth`

           :return: Success or failure
           :rtype: bool (True or False)
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/revoke_access_token.html

        """
        resp = self.session.get(self.revoke_access_token_url)
        LOGGER.debug(resp.text)
        resp.raise_for_status()

        return True
