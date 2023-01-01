# pyetrade

Python E-Trade API Wrapper
[![PyPI](https://img.shields.io/pypi/v/pyetrade.svg)](https://pypi.python.org/pypi/pyetrade)
[![PyPI](https://img.shields.io/pypi/l/pyetrade.svg)]()
[![PyPI](https://img.shields.io/pypi/pyversions/pyetrade.svg)](https://pypi.python.org/pypi/pyetrade)
[![Build Status](https://github.com/jessecooper/pyetrade/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/jessecooper/pyetrade/actions/workflows/build.yml/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/jessecooper/pyetrade/branch/master/graph/badge.svg)](https://codecov.io/gh/jessecooper/pyetrade)

This is a fork of the pyetrade project which adds the ability to automatically log in to an E-Trade account. The original repository left it up to the user to figure out how to automatically log in to their E-Trade account and required the user to manually log in to their account through the browser. This is obviously a problem if you are trying to deploy an automated trading program that can log in by itself. This fork provides a solution to that conundrum. However, as is mentioned in [#9](https://github.com/jessecooper/pyetrade/issues/9) and [#46](https://github.com/jessecooper/pyetrade/issues/46), automating login functions has security risks. You agree to bear these risks if you use any code from this repository. Keep your login credentials secure and follow cybersecurity best practices. 

## Completed
v1 API
Authorization API - ALL
Accounts
* List Accounts

Authorization API - ALL
Order API -
* List Orders
* Place Equity Order
* Cancel Order

Market API -
* Look Up Product
* Option Chain
* Get Quote

## Installation
### Install Package
```
pip install git+https://github.com/nathanramoscfa/pyetrade.git#egg=pyetrade
```
### Install Selenium WebDriver
This project requires the use of Selenium WebDriver in order to automatically log in to E-Trade through a browser. The browser can be [Chrome, Edge, Firefox, or Safari](https://selenium-python.readthedocs.io/installation.html#drivers), however, this project's code uses the [Microsoft Edge](https://www.microsoft.com/en-us/edge?exp=e502&form=MA13FJ) browser. Therefore, you will need to install the [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) to your project's directory. I have included a version "msedgedriver.exe" in the main directory of this repository, but, it needs to be the exact version that corresponds to your browser. I recommend you download the file directly from Microsoft using the instructions below. 

To install Selenium WebDriver:
1) Open your Microsoft Edge browser, select "Settings and more" at the top of the window, and then select "Settings". 
2) Scroll down and select "About Microsoft Edge". The version will be located towards the top. The Selenium WebDriver included in this project's root directory uses Microsoft Edge browser Version 108.0.1462.54 (Official build) (64-bit), and can only control this version of the browser. 
3) Go to Microsoft's official [webdriver page](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/). Download the Stable Channel version that corresponds to your version of the Microsoft Edge browser. From step 2, the version I would need to download is Version 108.0.1462.54: x64. This might be different for you so ensure you download the right version. 
4) Extract the "msedgedriver.exe" to the folder where your project is located. Ensure that the [executable path](https://github.com/nathanramoscfa/pyetrade/blob/master/pyetrade/authorization.py#L100) of "msedgedriver.exe" is correct. 

If you want to use another browser than Microsoft Edge, then you will have to repeat these steps for that browser. 

## Example Usage

WARNING - You accept all security and legal risks by using the code below. Keep your login credentials secure and follow cybersecurity best practices. To automatically log into ETrade:

```python
import pyetrade

consumer_key = "<CONSUMER_KEY>"
consumer_secret = "<SECRET_KEY>"

web_username = "<ETrade Username>"
web_password = "<ETrade Password>"

# Must obtain from ETrade Customer Service Technical Support Desk.
swh_cookie = {
    'name': '<COOKIE_NAME>',
    'value': '<COOKE_VALUE>',
    'domain': '.etrade.com',
    'secure': True,
    'httpOnly': True
}

oauth = pyetrade.ETradeOAuth(consumer_key, consumer_secret, web_username, web_password, swh_cookie)
verifier_code = oauth.get_verification_code(headless=False)
tokens = oauth.get_access_token(verifier_code)
print(tokens)
```

And then some the example code:

```python

accounts = pyetrade.ETradeAccounts(
    consumer_key,
    consumer_secret,
    tokens['oauth_token'],
    tokens['oauth_token_secret']
)

print(accounts.list_accounts())
```

## Documentation
[PyEtrade Documentation](https://pyetrade.readthedocs.io/en/latest/index.html)
## Contribute to pyetrade
* [ETrade API Docs](https://developer.etrade.com/home)
* Fork pyetrade
* Development Setup:
```
make init
make devel
```
or
```
pip install -r requirements.txt
pip install -r requirements_dev.txt
pip install -e .
```
* Lint
```
# Run Black
black pyetrade/
# Run Linter
pylint pyetrade/  #Lint score should be >=8
```
* Test
```
make test #Ensure test coverage is >80%
```
* Push Changes:
Push changes to a branch on your forked repo
* Create pull request
