# FastAPI X-Road SOAP

<img src="https://raw.githubusercontent.com/rik-ee/fastapi-xroad-soap/main/media/fxs_logo.jpg" alt="Logo" width="500">


[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-xroad-soap)](https://pypi.org/project/fastapi-xroad-soap/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/rik-ee/fastapi-xroad-soap/build-publish.yaml)](https://github.com/rik-ee/fastapi-xroad-soap/actions/workflows/build-publish.yaml)
[![codecov](https://codecov.io/gh/rik-ee/fastapi-xroad-soap/graph/badge.svg?token=KB58NGDC1N)](https://codecov.io/gh/rik-ee/fastapi-xroad-soap)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/fastapi-xroad-soap)](https://pypistats.org/packages/fastapi-xroad-soap)


[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=rik-ee_fastapi-xroad-soap&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=rik-ee_fastapi-xroad-soap)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=rik-ee_fastapi-xroad-soap&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=rik-ee_fastapi-xroad-soap)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=rik-ee_fastapi-xroad-soap&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=rik-ee_fastapi-xroad-soap)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=rik-ee_fastapi-xroad-soap&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=rik-ee_fastapi-xroad-soap)<br/>
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=rik-ee_fastapi-xroad-soap&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=rik-ee_fastapi-xroad-soap)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=rik-ee_fastapi-xroad-soap&metric=bugs)](https://sonarcloud.io/summary/new_code?id=rik-ee_fastapi-xroad-soap)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=rik-ee_fastapi-xroad-soap&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=rik-ee_fastapi-xroad-soap)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=rik-ee_fastapi-xroad-soap&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=rik-ee_fastapi-xroad-soap)


### Description

This library provides an extension to FastAPI, which allows FastAPI to be used as a SOAP service in the [X-Road](https://x-road.global/) data-exchange ecosystem. 
Internally, it utilizes the [pydantic-xml](https://pydantic-xml.readthedocs.io/en/latest/index.html#) library for data validation and conversion between XML structures and Python objects. 

The full documentation of this library can be found in the [Wiki](https://github.com/rik-ee/fastapi-xroad-soap/wiki).  


### Installation

Using PIP:
```shell
pip install fastapi-xroad-soap
```

Using Poetry:
```shell
poetry add fastapi-xroad-soap
```