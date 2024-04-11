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
import gc
import pytest
import string
import weakref
import typing as t
from fastapi_xroad_soap.utils import GlobalWeakStorage


__all__ = [
    "test_class_attributes",
    "test_instance_attributes",
    "test_unique_id_generation",
    "test_validate_fingerprint",
    "test_get_object_from_class",
    "test_get_object_from_instance",
    "test_get_object_with_bad_fingerprint",
    "test_object_persistence",
    "test_object_removal_on_reference_loss",
    "test_multiple_instances",
    "test_object_counter_increment",
    "test_instance_counter_wrap"
]


@pytest.fixture(scope="function")
def storage():
    return GlobalWeakStorage()


def test_class_attributes():
    assert hasattr(GlobalWeakStorage, "_unique_id")
    assert hasattr(GlobalWeakStorage, "validate_fingerprint")
    assert hasattr(GlobalWeakStorage, "retrieve_object")
    assert hasattr(GlobalWeakStorage, "_instances")
    assert hasattr(GlobalWeakStorage, "_inst_counter")
    assert hasattr(GlobalWeakStorage, "_uid")

    assert len(GlobalWeakStorage._instances) == 0
    assert GlobalWeakStorage._inst_counter == 0
    assert GlobalWeakStorage._uid == ''


def test_instance_attributes(storage):
    assert hasattr(storage, "_objects")
    assert hasattr(storage, "_obj_counter")
    assert hasattr(storage, "retrieve_object")
    assert hasattr(storage, "insert_object")
    assert hasattr(storage, "get")

    assert len(storage._objects) == 0
    assert storage._obj_counter == 0
    assert storage._uid != ''


def test_unique_id_generation():
    uid = GlobalWeakStorage._unique_id(123)

    assert isinstance(uid, str)
    assert len(uid) == 59
    assert '..' in uid

    counter, token = uid.split('..')  # type: str, str
    assert len(counter) == 9
    assert len(token) == 48
    assert counter.isdigit()

    valid_b64_chars = string.ascii_letters + string.digits + '+/='
    for char in token:
        assert char in valid_b64_chars

    uid2 = GlobalWeakStorage._unique_id(124)
    assert uid != uid2


def test_validate_fingerprint(storage):
    uid = storage._unique_id(123)
    good_fp = f"{uid}-$$-{uid}"

    bad_fingerprints = [
        t.cast(str, 123),  # bad type
        good_fp[:-1],  # too short
        good_fp + 'a',  # too long
        good_fp.replace('-$$-', '~%%~'),  # bad separator
        f"{uid[:-1]}-$$-{uid}",  # partial too short
        f"{uid}-$$-{uid + 'a'}",  # partial too long
    ]
    for bad_fp in bad_fingerprints:
        with pytest.raises(ValueError):
            storage.validate_fingerprint(bad_fp)

    counter, token = uid.split('..')  # type: str, str
    with pytest.raises(ValueError):
        bad_uid = f"{counter}..{token + 'A'}"  # uid too long
        bad_fp = f"{bad_uid}-$$-{bad_uid[:-2]}"
        storage.validate_fingerprint(bad_fp)
    bad_unique_ids = [
        f"{counter}##{token}",  # bad separator
        f"{counter + '0'}..{token[:-1]}",  # counter too long
        f"{counter[:-1] + 'A'}..{token}",  # not a digit in counter
        f"{counter}..{token[:-1] + '@'}"  # not a hex char in token
    ]
    for bad_uid in bad_unique_ids:
        with pytest.raises(ValueError):
            bad_fp = f"{bad_uid}-$$-{bad_uid}"
            storage.validate_fingerprint(bad_fp)


def test_get_object_from_class(storage):
    test_obj = {1, 2, 3}
    fingerprint = storage.insert_object(test_obj)
    returned_obj = GlobalWeakStorage.retrieve_object(fingerprint)
    assert returned_obj == test_obj


def test_get_object_from_instance(storage):
    test_obj = {1, 2, 3}
    fingerprint = storage.insert_object(test_obj)
    returned_obj = storage.get(fingerprint)
    assert returned_obj == test_obj


def test_get_object_with_bad_fingerprint(storage):
    bad_fp = "invalid-$$-fingerprint"
    with pytest.raises(ValueError):
        GlobalWeakStorage.retrieve_object(bad_fp)
    with pytest.raises(ValueError):
        storage.get(bad_fp)


def test_object_persistence(storage):
    test_obj = {1, 2, 3}
    fingerprint = storage.insert_object(test_obj)
    returned_obj = storage.retrieve_object(fingerprint)
    assert returned_obj is test_obj
    assert weakref.getweakrefcount(test_obj) > 0


def test_object_removal_on_reference_loss(storage):
    def insert_obj():
        test_obj = {1, 2, 3}
        return storage.insert_object(test_obj)

    fingerprint = insert_obj()
    gc.collect()
    retrieved_obj = storage.retrieve_object(fingerprint, raise_on_miss=False)
    assert retrieved_obj is None

    with pytest.raises(KeyError):
        storage.retrieve_object(fingerprint, raise_on_miss=True)


def test_multiple_instances():
    storage1 = GlobalWeakStorage()
    storage2 = GlobalWeakStorage()

    assert storage1._uid != storage2._uid

    test_obj1 = {1, 2, 3}
    test_obj2 = {4, 5, 6}
    fingerprint1 = storage1.insert_object(test_obj1)
    fingerprint2 = storage2.insert_object(test_obj2)
    assert fingerprint1 != fingerprint2

    assert storage1.get(fingerprint1) == test_obj1
    assert storage2.get(fingerprint2) == test_obj2

    assert storage1.get(fingerprint2, raise_on_miss=False) is None
    assert storage2.get(fingerprint1, raise_on_miss=False) is None

    with pytest.raises(KeyError):
        storage1.get(fingerprint2, raise_on_miss=True)
    with pytest.raises(KeyError):
        storage2.get(fingerprint1, raise_on_miss=True)

    assert GlobalWeakStorage._instances.get(storage1._uid) is not None
    assert GlobalWeakStorage._instances.get(storage2._uid) is not None


def test_object_counter_increment(storage):
    initial_counter = storage._obj_counter
    test_obj = {1, 2, 3}
    storage.insert_object(test_obj)
    assert storage._obj_counter == initial_counter + 1


def test_instance_counter_wrap():
    GlobalWeakStorage._inst_counter = 999999999
    GlobalWeakStorage()
    _storage = GlobalWeakStorage()
    uid = _storage._uid.split('..')[0]
    assert all(c == '0' for c in uid)
    GlobalWeakStorage._inst_counter = 0
