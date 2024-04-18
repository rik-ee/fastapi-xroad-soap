# Changelog

All notable changes to this project will be documented in this file.  
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).  
_NOTE: This changelog is generated and managed by [devtools-cli](https://pypi.org/project/devtools-cli/), **do not edit manually**._


### [0.3.0] - 2024-04-18 - _latest_

- UIDGenerator is now able to work in deterministic mode
- SoapAction now enforces action name type and length restrictions
- Improved parsing of SOAP actions from HTTP headers
- Length restriction now overrides min and max length in StringTypeSpec
- Added WSDL generator and its helpers module
- Improved fault error messages
- Library now disallows extra elements when endpoint handler has body model parameter defined
- Many bug fixes

### [0.2.2] - 2024-04-14

- Improved maintainability
- Reduced cognitive complexity of some functions
- Fixed error propagation bug in SoapAction
- Fixed reluctant quantifier issue in regex pattern
- Remediated polynomial runtime regex security hotspot

### [0.2.1] - 2024-04-14

- Updated dependencies
- Fixed pytests and GHA workflows

### [0.2.0] - 2024-04-13

- Almost full functionality (TODO: wsdl generation)
- Added PyPI publishing workflow
- Bumped project status to Beta
- Added basic README.md content

### [0.1.0] - 2024-03-20

- Initialized project

[0.3.0]: https://github.com/rik-ee/fastapi-xroad-soap/compare/0.2.2...0.3.0
[0.2.2]: https://github.com/rik-ee/fastapi-xroad-soap/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/rik-ee/fastapi-xroad-soap/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/rik-ee/fastapi-xroad-soap/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/rik-ee/fastapi-xroad-soap/compare/0.1.0...0.1.0