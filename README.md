# pyetrade

Python E-Trade API Wrapper
[![PyPI](https://img.shields.io/pypi/v/pyetrade.svg)](https://pypi.python.org/pypi/pyetrade)
[![PyPI](https://img.shields.io/pypi/l/pyetrade.svg)]()
[![PyPI](https://img.shields.io/pypi/pyversions/pyetrade.svg)](https://pypi.python.org/pypi/pyetrade)
[![Build Status](https://github.com/jessecooper/pyetrade/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/jessecooper/pyetrade/actions/workflows/build.yml/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/jessecooper/pyetrade/branch/master/graph/badge.svg)](https://codecov.io/gh/jessecooper/pyetrade)

This is a fork of the pyetrade project which adds the ability to automatically log in to an E-Trade account. The original repository left it up to the user to figure out how to automatically log in to their E-Trade account and required the user to manually log in to their account through the browser. This is obviously a problem if you are trying to deploy an automated trading program that can log in by itself. This fork provides a solution to that conundrum. However, as is mentioned in [#9](https://github.com/jessecooper/pyetrade/issues/9) and [#46](https://github.com/jessecooper/pyetrade/issues/46), automating login functions has security and possible legal risks. You agree to bear these risks if you use any code from this repository. Keep your login credentials secure and follow cybersecurity best practices. 

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

## Install
```
git clone https://github.com/jessecooper/pyetrade.git
```
## Example Usage

To automatically log into ETrade:
```python
import pyetrade

consumer_key = "<CONSUMER_KEY>"
consumer_secret = "<SECRET_KEY>"

web_username = "<ETrade Username>"
web_password = "<ETrade Password>"

# Must obtain from ETrade Customer Service Technical
# Support Desk.
swh_cookie = {
    'name': '<COOKIE_NAME>',
    'value': '<COOKE_VALUE>',
    'domain': '.etrade.com',
    'secure': True,
    'httpOnly': True
}

oauth = pyetrade.ETradeOAuth(consumer_key, consumer_secret, web_username, web_password, swh_cookie)
verifier_code = oauth.get_verification_code()
tokens = oauth.get_access_token(verifier_code)
print(tokens)
```

Once logged in, perform actions such as listing accounts:

```
accounts = pyetrade.ETradeAccounts(
    consumer_key,
    consumer_secret,
    tokens['oauth_token'],
    tokens['oauth_token_secret']
)

print(accounts.list_accounts())
```

## Documentation
[PyEtrade Documentation](https://pyetrade.readthedocs.io/en/latest/)
## Contribute to pyetrade
* [ETrade API Docs](https://developer.etrade.com/ctnt/dev-portal/getArticleByCategory?category=Documentation)
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
