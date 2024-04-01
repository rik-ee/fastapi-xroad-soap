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
import weakref
from fastapi_xroad_soap.internal.storage import GlobalWeakStorage


@pytest.fixture(scope="function")
def storage():
    return GlobalWeakStorage()


def test_instance_creation(storage):
    assert storage is not None
    assert hasattr(storage, '_uid')
    assert storage._uid != '', "Instance should have a non-empty unique identifier"


def test_unique_id_generation():
    first_id = GlobalWeakStorage._unique_id(0)
    second_id = GlobalWeakStorage._unique_id(1)

    assert isinstance(first_id, str)
    assert '..' in first_id, "ID should contain '..'"
    assert first_id.split('..')[0].isdigit(), "The part before '..' should be digits"
    assert len(first_id.split('..')[1]) == 48, "The part after '..' should be 24 hex chars (48 chars)"
    assert first_id != second_id, "IDs should be unique"


def test_insert_object(storage):
    test_obj = {1, 2, 3}
    fingerprint = storage.insert_object(test_obj)

    assert isinstance(fingerprint, str), "Fingerprint must be a string"
    assert '-$$-' in fingerprint, "Fingerprint format is incorrect"

    retrieved_obj = storage.retrieve_object(fingerprint)
    assert retrieved_obj == test_obj, "The retrieved object does not match the inserted object"


def test_retrieve_object_with_valid_fingerprint(storage):
    test_obj = {1, 2, 3}
    fingerprint = storage.insert_object(test_obj)
    retrieved_obj = GlobalWeakStorage.retrieve_object(fingerprint)
    assert retrieved_obj == test_obj, "The retrieved object should match the inserted object"


def test_retrieve_object_with_invalid_fingerprint(storage):
    invalid_fingerprint = "invalid-$$-fingerprint"
    retrieved_obj = GlobalWeakStorage.retrieve_object(invalid_fingerprint)
    assert retrieved_obj is None, "Retrieving with an invalid fingerprint should return None"


def test_object_persistence(storage):
    test_obj = {1, 2, 3}
    obj_fingerprint = storage.insert_object(test_obj)

    retrieved_obj = storage.retrieve_object(obj_fingerprint)
    assert retrieved_obj is test_obj, "The object should persist in the storage while referenced."
    assert weakref.getweakrefcount(test_obj) > 0, "Object should have weak references."


def test_object_removal_on_reference_loss(storage):
    def insert_obj():
        test_obj = {1, 2, 3}
        return storage.insert_object(test_obj)

    fingerprint = insert_obj()
    gc.collect()

    retrieved_obj = storage.retrieve_object(fingerprint)
    assert retrieved_obj is None, \
        "The object should be removed from storage after losing all external references"


def test_multiple_instances():
    storage1 = GlobalWeakStorage()
    storage2 = GlobalWeakStorage()

    assert storage1._uid != storage2._uid, "Each instance should have a unique UID"

    test_obj1 = {1, 2, 3}
    test_obj2 = {4, 5, 6}
    fingerprint1 = storage1.insert_object(test_obj1)
    fingerprint2 = storage2.insert_object(test_obj2)

    assert storage1.get(fingerprint1) == test_obj1, \
        "Instance 1 should retrieve the correct object using its fingerprint"
    assert storage2.get(fingerprint2) == test_obj2, \
        "Instance 2 should retrieve the correct object using its fingerprint"

    assert fingerprint1 != fingerprint2, "Fingerprints should be unique across instances"

    assert storage1.get(fingerprint2) is None, \
        "Must not be able to retrieve storage2 file from storage1"
    assert storage2.get(fingerprint1) is None, \
        "Must not be able to retrieve storage1 file from storage2"

    assert GlobalWeakStorage._instances.get(storage1._uid) is not None, \
        "Instance 1 should be retrievable from the class-wide instance store"
    assert GlobalWeakStorage._instances.get(storage2._uid) is not None, \
        "Instance 2 should be retrievable from the class-wide instance store"


def test_object_counter_increment(storage):
    initial_counter = storage._obj_counter
    test_obj = {1, 2, 3}
    storage.insert_object(test_obj)
    assert storage._obj_counter == initial_counter + 1, \
        "Object counter should increment by 1 after insertion."


def test_instance_counter_wrap():
    GlobalWeakStorage._inst_counter = 999999999
    GlobalWeakStorage()
    storage = GlobalWeakStorage()
    uid = storage._uid.split('..')[0]
    assert all(c == '0' for c in uid)
    GlobalWeakStorage._inst_counter = 0


def test_get_method_with_object_id():
    storage = GlobalWeakStorage()
    test_obj = {1, 2, 3}
    fingerprint = storage.insert_object(test_obj)
    obj_id = fingerprint.split('-$$-')[1]
    retrieved_obj = storage.get(obj_id)
    assert retrieved_obj == test_obj, \
        "Object should be retrievable with its object ID."


def test_get_method_with_full_fingerprint():
    storage = GlobalWeakStorage()
    test_obj = {1, 2, 3}
    fingerprint = storage.insert_object(test_obj)
    retrieved_obj = storage.get(fingerprint)
    assert retrieved_obj == test_obj, \
        "Object should be retrievable with its full fingerprint."


def test_get_method_with_invalid_id():
    storage = GlobalWeakStorage()
    invalid_fingerprint = '123-$$-456'
    result = storage.get(invalid_fingerprint)
    assert result is None, \
        "Method should return None for an invalid ID."
