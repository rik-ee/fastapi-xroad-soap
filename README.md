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

By convention until now, creating a well-working SOAP service has been a difficult undertaking due to the inherent complexity 
of the SOAP specification, which is further exacerbated by the constraints and requirements of the [X-Road](https://x-road.global/) data-exchange ecosystem. 
This library remediates this issue by providing excellent batteries-included developer experience for solving the most complex tasks related to the subject. 
Creating an X-Road SOAP service does not have to be difficult or time-consuming ever again. 


### Features

- Extension of FastAPI, which integrates well with the existing FastAPI ecosystem
- Definition of requests and responses using ORM-like models syntax
- Automatic validation of request and response elements and data types
- Automatic WSDL file generation from defined models
- Support for sync and async endpoint handlers
- Built-in endpoint for serving the generated WSDL file
- Built-in Fault response error messages
- Excellent pytest coverage and code quality
- Plentiful examples and documentation
- Developer-oriented ease of use


### Quickstart


Install the library from [PyPI](https://pypi.org/project/fastapi-xroad-soap/). We recommend to use the [Poetry](https://python-poetry.org/) or the [PIP](https://pip.pypa.io/en/stable/) package manager: 

```shell
poetry add fastapi-xroad-soap
```
```shell
pip install fastapi-xroad-soap
```

_**Note 1:**_ You also need to install an ASGI web server library like [Uvicorn](https://www.uvicorn.org/) to run the SoapService FastAPI app.  
_**Note 2:**_ You also need a third-party application for making HTTP requests. The most widely used application for testing SOAP services is [SoapUI](https://www.soapui.org/tools/soapui/) by SmartBear, but 
you can also use any other software like [Postman](https://www.postman.com/downloads/) or [Insomnia](https://insomnia.rest/download). 
The main requirement for the software is that it must support setting custom request headers and making HTTP POST requests with raw body content. 

Next, create a `.py` file with the following contents:
```python
import uvicorn
from fastapi_xroad_soap import SoapService, MessageBody
from fastapi_xroad_soap.elements import Integer

soap = SoapService()

class Model(MessageBody):
    number = Integer()

@soap.action("ReturnInteger")
def handler(body: Model) -> Model:
    return Model(number=body.number)

uvicorn.run(soap)
```

This simple service just returns the integer from the client request back to the client. 
When you run the script and navigate to `http://localhost:8000/service?wsdl` in your web browser, 
you should see the generated WSDL file that corresponds to the `SoapService` instance.


### Making a Request

If you're using SoapUI for API testing, it is suggested to import the autogenerated WSDL file of the service 
into SoapUI, as that will enable SoapUI to autogenerate example requests for the defined services and skip the 
manual setting of the necessary HTTP headers, you just need to fill in the placeholders with valid values. 
In other cases, read on how to manually craft a valid request for the example service. 

In your chosen API testing software, create a new POST request and set the following custom headers: 
1) Key: `SOAPAction`, Value: `ReturnInteger`
2) Key: `Content-Type`, Value: `text/xml`

Set the following XML as the raw body and send the request: 
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <Model>
            <Number>1234</Number>
        </Model>
    </soapenv:Body>
</soapenv:Envelope>
```

You should receive the following response if everything is working as expected:
```xml
<?xml version='1.0' encoding='utf-8' standalone='yes'?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <Model>
            <Number>1234</Number>
        </Model>
    </soapenv:Body>
</soapenv:Envelope>
```

### Next Steps

1) Try out the other examples in the [examples](https://github.com/rik-ee/fastapi-xroad-soap/tree/main/examples) directory.  
2) Read the full documentation and API reference in the [Wiki](https://github.com/rik-ee/fastapi-xroad-soap/wiki).  
3) Build something awesome with this library!


### Credits

[Centre of Registers and Information Systems](https://www.rik.ee/en)
