# OAIBridge

[![Build Status](https://travis-ci.org/luskaner/oai-bridge.svg?branch=master)](https://travis-ci.org/luskaner/oai-bridge)

OAI Bridge that allows DSpace to harvest multiple collections/communities to a single internal collection or simply expose multiple servers (remote or local) and sets as a single context.

## Requirements

### Release

* Python 3.6+ with the following packages:
  * Flask 1+
    * flask_caching  
  * lxml
  * requests
  * yaml
* *WGSI server*

*Note: Python packages can be installed with `pip3 install -r requirements.txt`*

### Testing (*in addition, except the WGSI server*)

Install them with `pip3 install -r requirements.test.txt`

* flask_testing
* Sickle
* timeout_decorator

## Configuration

1. Rename `configuration.template.yaml` to `configuration.yaml`.
2. Modify `configuration.yaml` as per the file instructions.

*Note: Run in production with your choosen WGSI server or in debug mode with [Flask instructions](http://flask.pocoo.org/docs/1.0/quickstart/).*

## Tests

The tests compare the results between the direct OAI responses and this bridge using *Sickle*.

* `TestStaticListRecords`: Does a test with a curated list of servers with various parameters.
* `TestDynamicListRecords`: Same as before but with randoms servers from http://www.openarchives.org/pmh/registry/ListFriends and random configuration. *Note: this test is very prone to fail.*

*Note: This tests might fail due to a timeout specified.*

### Running

Run the tests following the [official python documentation](https://docs.python.org/3/library/unittest.html#command-line-interface).
