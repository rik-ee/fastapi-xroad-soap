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
import typing as t
from fastapi_xroad_soap.internal.constants import ENV_NSMAP
from fastapi_xroad_soap.internal.envelope.base import Element, Attribute, BaseXmlModel


__all__ = ["XroadHeaderService", "XroadHeaderClient", "XroadHeader"]


class XroadHeaderService(BaseXmlModel, tag="service", ns="xroad", nsmap=ENV_NSMAP):
	object_type: str = Attribute(tag="objectType", ns="xid", default="SERVICE")
	xroad_instance: str = Element(tag="xRoadInstance", ns="xid")
	member_class: str = Element(tag="memberClass", ns="xid")
	member_code: str = Element(tag="memberCode", ns="xid")
	subsystem_code: t.Union[str, None] = Element(tag="subsystemCode", ns="xid", default=None)
	service_code: str = Element(tag="serviceCode", ns="xid")
	service_version: t.Union[str, None] = Element(tag="serviceVersion", ns="xid", default=None)


class XroadHeaderClient(BaseXmlModel, tag="client", ns="xroad", nsmap=ENV_NSMAP):
	object_type: str = Attribute(tag="objectType", ns="xid", default="SUBSYSTEM")
	xroad_instance: str = Element(tag="xRoadInstance", ns="xid")
	member_class: str = Element(tag="memberClass", ns="xid")
	member_code: str = Element(tag="memberCode", ns="xid")
	subsystem_code: t.Union[str, None] = Element(tag="subsystemCode", ns="xid", default=None)


class XroadHeader(BaseXmlModel, tag="Header", ns="soapenv", nsmap=ENV_NSMAP):
	proto_ver: str = Element(tag="protocolVersion", ns="xroad")
	user_id: t.Union[str, None] = Element(tag="userId", ns="xroad", default=None)
	id: str = Element(tag="id", ns="xroad")
	service: t.Union[XroadHeaderService, None] = None
	client: XroadHeaderClient
