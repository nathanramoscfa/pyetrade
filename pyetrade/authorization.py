"""Authorization - ETrade Authorization API Calls"""

import logging
from requests_oauthlib import OAuth1Session

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Set up logging
LOGGER = logging.getLogger(__name__)


class ETradeOAuth(object):
    """:description: Performs authorization for OAuth 1.0a

       :param client_key: Client key provided by Etrade
       :type client_key: str, required
       :param client_secret: Client secret provided by Etrade
       :type client_secret: str, required
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

    def get_request_token(self):
        """:description: Obtains the token URL from Etrade.

           :param None: Takes no parameters
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

    def get_verification_code(self, dev, headless=False, browser='chrome'):
        """:description: Obtains verification code for signing into E-Trade.

           :param dev: Option to use development API, defaults to False
           :type dev: bool, optional
           :param headless: Option to run browser in headless mode, defaults to False
           :type headless: bool, optional
           :param browser: Browser to use for automation, defaults to 'chrome'
           :type browser: str, optional
           :return: Verification code (Used for two-factor authentication)
           :rtype: str

        """

        formated_auth_url = self.get_request_token()

        # Automate the login process
        if browser == 'chrome':
            options = webdriver.ChromeOptions()
            if headless:
                options.headless = True
            service = Service(executable_path='chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=options)

        elif browser == 'edge':
            options = webdriver.EdgeOptions()
            if headless:
                options.headless = True
            service = Service(executable_path='msedgedriver.exe')
            driver = webdriver.Edge(service=service, options=options)

        driver.get(formated_auth_url)

        driver.add_cookie(self.etrade_cookie)

        user_id = driver.find_element(By.NAME, 'USER')
        user_id.send_keys(self.web_username)

        password = driver.find_element(By.NAME, 'PASSWORD')
        password.send_keys(self.web_password)

        logon = driver.find_element(By.ID, 'logon_button')
        logon.click()

        driver.implicitly_wait(5)

        try:
            accept = driver.find_element(By.NAME, "submit")
            accept.click()
        except NoSuchElementException:
            driver.close()

        verifier = driver.find_element(By.XPATH, "//div[@style='text-align:center']/input[1]")
        verifier = verifier.get_attribute('value')

        driver.close()

        return verifier

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
        self.revoke_access_token_url = (
            r"https://api.etrade.com/oauth/revoke_access_token"
        )
        self.session = OAuth1Session(
            self.client_key,
            self.client_secret,
            self.resource_owner_key,
            self.resource_owner_secret,
            signature_type="AUTH_HEADER",
        )

    def renew_access_token(self):
        """:description: Renews access tokens obtained from :class:`ETradeOAuth`

           :param None: Takes no parameters
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

           :param None: Takes no parameters
           :return: Success or failure
           :rtype: bool (True or False)
           :EtradeRef: https://apisb.etrade.com/docs/api/authorization/revoke_access_token.html

        """
        resp = self.session.get(self.revoke_access_token_url)
        LOGGER.debug(resp.text)
        resp.raise_for_status()

        return True
