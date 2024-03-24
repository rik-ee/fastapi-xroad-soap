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
from fastapi_xroad_soap.internal.wsdl.models.binding import (
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
from fastapi_xroad_soap.internal.wsdl.models.conditions import (
	Enumeration,
	RegexPattern,
	MinInclusive,
	MaxInclusive,
	MinExclusive,
	MaxExclusive,
	FractionDigits,
	TotalDigits,
	Length,
	MinLength,
	MaxLength,
	WhiteSpace
)
from fastapi_xroad_soap.internal.wsdl.models.definitions import (
	WSDLTypes,
	WSDLPart,
	WSDLMessage,
	WSDLDefinitions
)
from fastapi_xroad_soap.internal.wsdl.models.port_type import (
	WSDLFaultPort,
	WSDLOutputPort,
	WSDLInputPort,
	WSDLDocumentation,
	WSDLOperationPort,
	WSDLPortType
)
from fastapi_xroad_soap.internal.wsdl.models.restrictions import (
	StringRestriction,
	IntegerRestriction,
	DecimalRestriction,
	FloatRestriction,
	DoubleRestriction,
	DateRestriction,
	TimeRestriction,
	DateTimeRestriction,
	DurationRestriction,
	AnyURIRestriction
)
from fastapi_xroad_soap.internal.wsdl.models.schema import (
	SimpleType,
	AnyXML,
	Element,
	Sequence,
	ComplexType,
	Import,
	Include,
	Schema
)
from fastapi_xroad_soap.internal.wsdl.models.service import (
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
	"MinExclusive",
	"MaxExclusive",
	"FractionDigits",
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
	"StringRestriction",
	"IntegerRestriction",
	"DecimalRestriction",
	"FloatRestriction",
	"DoubleRestriction",
	"DateRestriction",
	"TimeRestriction",
	"DateTimeRestriction",
	"DurationRestriction",
	"AnyURIRestriction",

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
