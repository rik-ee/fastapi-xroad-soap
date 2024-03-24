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


class XroadHeaderService(BaseXmlModel, tag="service", ns="xro", nsmap=ENV_NSMAP, search_mode='unordered'):
	object_type: str = Attribute(tag="objectType", ns="iden", default="SERVICE")
	xroad_instance: str = Element(tag="xRoadInstance", ns="iden")
	member_class: str = Element(tag="memberClass", ns="iden")
	member_code: str = Element(tag="memberCode", ns="iden")
	subsystem_code: t.Union[str, None] = Element(tag="subsystemCode", ns="iden", default=None)
	service_code: str = Element(tag="serviceCode", ns="iden")
	service_version: t.Union[str, None] = Element(tag="serviceVersion", ns="iden", default=None)


class XroadHeaderClient(BaseXmlModel, tag="client", ns="xro", nsmap=ENV_NSMAP, search_mode='unordered'):
	object_type: str = Attribute(tag="objectType", ns="iden", default="SUBSYSTEM")
	xroad_instance: str = Element(tag="xRoadInstance", ns="iden")
	member_class: str = Element(tag="memberClass", ns="iden")
	member_code: str = Element(tag="memberCode", ns="iden")
	subsystem_code: t.Union[str, None] = Element(tag="subsystemCode", ns="iden", default=None)


class XroadHeader(BaseXmlModel, tag="Header", ns="soapenv", nsmap=ENV_NSMAP, search_mode='unordered'):
	user_id: t.Union[str, None] = Element(tag="userId", ns="xro", default=None)
	proto_ver: str = Element(tag="protocolVersion", ns="xro")
	id: str = Element(tag="id", ns="xro")
	service: t.Union[XroadHeaderService, None] = None
	client: XroadHeaderClient
