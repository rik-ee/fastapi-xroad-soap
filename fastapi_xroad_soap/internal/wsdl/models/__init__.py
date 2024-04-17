#
#   European Union Public License 1.2
#
#   Copyright (c) 2024, Centre of Registers and Information Systems
#
#   The contents of this file are subject to the terms and conditions defined in the License.
#   You may not use, modify, or distribute this file except in compliance with the License.
#
#   SPDX-License-Identifier: EUPL-1.2
#
from .binding import (
	SOAPFault,
	SOAPBody,
	SOAPHeader,
	WSDLFaultBinding,
	WSDLOutputBinding,
	WSDLInputBinding,
	XROADVersion,
	SOAPOperationBinding,
	WSDLOperationBinding,
	SOAPBinding,
	WSDLBinding
)
from .conditions import (
	Enumeration,
	RegexPattern,
	MinInclusive,
	MaxInclusive,
	TotalDigits,
	Length,
	MinLength,
	MaxLength,
	WhiteSpace,
)
from .definitions import (
	WSDLTypes,
	WSDLPart,
	WSDLMessage,
	WSDLDefinitions,
)
from .port_type import (
	WSDLFaultPort,
	WSDLOutputPort,
	WSDLInputPort,
	WSDLDocumentation,
	WSDLOperationPort,
	WSDLPortType,
)
from .restrictions import (
	NumericTypeRestriction,
	StringTypeRestriction
)
from .schema import (
	SimpleType,
	AnyXML,
	Element,
	Sequence,
	ComplexType,
	Import,
	Include,
	Schema
)
from .service import (
	SOAPAddress,
	WSDLPortBinding,
	WSDLService
)


__all__ = [
	# binding.py
	"SOAPFault",
	"SOAPBody",
	"SOAPHeader",
	"WSDLFaultBinding",
	"WSDLOutputBinding",
	"WSDLInputBinding",
	"XROADVersion",
	"SOAPOperationBinding",
	"WSDLOperationBinding",
	"SOAPBinding",
	"WSDLBinding",

	# conditions.py
	"Enumeration",
	"RegexPattern",
	"MinInclusive",
	"MaxInclusive",
	"TotalDigits",
	"Length",
	"MinLength",
	"MaxLength",
	"WhiteSpace",

	# definitions.py
	"WSDLTypes",
	"WSDLPart",
	"WSDLMessage",
	"WSDLDefinitions",

	# port_type.py
	"WSDLFaultPort",
	"WSDLOutputPort",
	"WSDLInputPort",
	"WSDLDocumentation",
	"WSDLOperationPort",
	"WSDLPortType",

	# restrictions.py
	"NumericTypeRestriction",
	"StringTypeRestriction",

	# schema.py
	"SimpleType",
	"AnyXML",
	"Element",
	"Sequence",
	"ComplexType",
	"Import",
	"Include",
	"Schema",

	# service.py
	"SOAPAddress",
	"WSDLPortBinding",
	"WSDLService"
]
