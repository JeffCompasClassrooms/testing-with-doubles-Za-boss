import os
import pytest
from mydb import MyDB
from unittest.mock import call

todo = pytest.mark.skip(reason='todo: pending spec')

def describe_MyDB():

    @pytest.fixture(autouse=True, scope="session")
    def verify_filesystem_is_not_touched():
        yield
        assert not os.path.isfile("mydatabase.db")

    def describe_init():
        def it_assigns_fname_attribute(mocker):
            mocker.patch("os.path.isfile", return_value=True)
            db = MyDB("mydatabase.db")
            assert db.fname == "mydatabase.db"

        def it_creates_empty_database_if_it_does_not_exist(mocker):
            # set up stubs & mocks first
            mock_isfile = mocker.patch("os.path.isfile", return_value=False)
            mock_open = mocker.patch("builtins.open", mocker.mock_open())
            mock_dump = mocker.patch("pickle.dump")

            # execute on the test subject
            db = MyDB("mydatabase.db")

            # assert what happened
            mock_isfile.assert_called_once_with("mydatabase.db")
            mock_open.assert_called_once_with("mydatabase.db", "wb")
            mock_dump.assert_called_once_with([], mock_open.return_value)

        @todo
        def it_does_not_create_database_if_it_already_exists(mocker):
            pass
    
    def describe_loadStrings():
        @todo
        def it_loads_an_array_from_a_file_and_returns_it(mocker):
            pass
    def describe_saveStrings():
        @todo
        def it_saves_the_given_array_to_a_file(mocker):
            pass
    
    def describe_saveString():
        @todo
        def it_appends_string_element_to_existing_database(mocker):
            pass