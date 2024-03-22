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
from typing import Union
from pydantic_xml import BaseXmlModel, element, attr
from src.constants import ENV_NSMAP


__all__ = ["XroadHeaderService", "XroadHeaderClient", "XroadHeader"]


class XroadHeaderService(BaseXmlModel, tag="service", ns="xroad", nsmap=ENV_NSMAP):
	object_type: str = attr(tag="objectType", ns="xid", default="SERVICE")
	xroad_instance: str = element(tag="xRoadInstance", ns="xid")
	member_class: str = element(tag="memberClass", ns="xid")
	member_code: str = element(tag="memberCode", ns="xid")
	subsystem_code: Union[str, None] = element(tag="subsystemCode", ns="xid", default=None)
	service_code: str = element(tag="serviceCode", ns="xid")
	service_version: Union[str, None] = element(tag="serviceVersion", ns="xid", default=None)


class XroadHeaderClient(BaseXmlModel, tag="client", ns="xroad", nsmap=ENV_NSMAP):
	object_type: str = attr(tag="objectType", ns="xid", default="SUBSYSTEM")
	xroad_instance: str = element(tag="xRoadInstance", ns="xid")
	member_class: str = element(tag="memberClass", ns="xid")
	member_code: str = element(tag="memberCode", ns="xid")
	subsystem_code: Union[str, None] = element(tag="subsystemCode", ns="xid", default=None)


class XroadHeader(BaseXmlModel, tag="Header", ns="soapenv", nsmap=ENV_NSMAP):
	proto_ver: str = element(tag="protocolVersion", ns="xroad")
	user_id: Union[str, None] = element(tag="userId", ns="xroad", default=None)
	id: str = element(tag="id", ns="xroad")
	service: Union[XroadHeaderService, None] = None
	client: XroadHeaderClient
