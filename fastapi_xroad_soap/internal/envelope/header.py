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
from pydantic_xml import BaseXmlModel, element, attr
from ..constants import HEADER_NSMAP


__all__ = ["XroadService", "XroadClient", "XroadHeader"]


class XroadService(BaseXmlModel, tag="service", ns="xro", nsmap=HEADER_NSMAP, search_mode='unordered'):
	object_type: str = attr(tag="objectType", ns="iden", default="SERVICE")
	xroad_instance: str = element(tag="xRoadInstance", ns="iden")
	member_class: str = element(tag="memberClass", ns="iden")
	member_code: str = element(tag="memberCode", ns="iden")
	subsystem_code: t.Union[str, None] = element(tag="subsystemCode", ns="iden", default=None)
	service_code: str = element(tag="serviceCode", ns="iden")
	service_version: t.Union[str, None] = element(tag="serviceVersion", ns="iden", default=None)


class XroadClient(BaseXmlModel, tag="client", ns="xro", nsmap=HEADER_NSMAP, search_mode='unordered'):
	object_type: str = attr(tag="objectType", ns="iden", default="SUBSYSTEM")
	xroad_instance: str = element(tag="xRoadInstance", ns="iden")
	member_class: str = element(tag="memberClass", ns="iden")
	member_code: str = element(tag="memberCode", ns="iden")
	subsystem_code: t.Union[str, None] = element(tag="subsystemCode", ns="iden", default=None)


class XroadHeader(BaseXmlModel, tag="Header", ns="soapenv", nsmap=HEADER_NSMAP, search_mode='unordered'):
	user_id: t.Union[str, None] = element(tag="userId", ns="xro", default=None)
	proto_ver: str = element(tag="protocolVersion", ns="xro")
	id: str = element(tag="id", ns="xro")
	service: t.Union[XroadService, None] = None
	client: XroadClient
