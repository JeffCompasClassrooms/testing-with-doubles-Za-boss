import os
import pytest
from mydb import MyDB
from unittest.mock import call, patch, mock_open

todo = pytest.mark.skip(reason='todo: pending spec')
#I think it's a good idea to fixture these things, but idk how to go about doing it
@pytest.fixture
def mock_isfile_false():
    with patch("os.path.isfile", return_value=False) as m:
        yield m

@pytest.fixture
def mock_isfile_true():
    with patch("os.path.isfile", return_value=True) as m:
        yield m

@pytest.fixture
def mock_open_func():
    with patch("builtins.open", mock_open()) as m:
        yield m

@pytest.fixture
def mock_dump_func():
    with patch("pickle.dump") as m:
        yield m
        
@pytest.fixture
def mock_load():
    with patch("pickle.load", return_value=[]) as m:
        yield m

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

        def it_creates_empty_database_if_it_does_not_exist(mock_isfile_false, mock_open_func, mock_dump_func):
            # set up stubs & mocks first
            # execute on the test subject
            db = MyDB("mydatabase.db")

            # assert what happened
            mock_isfile_false.assert_called_once_with("mydatabase.db")
            mock_open_func.assert_called_once_with("mydatabase.db", "wb")
            mock_dump_func.assert_called_once_with([], mock_open_func())

        def it_does_not_create_database_if_it_already_exists(mock_isfile_true, mock_open_func, mock_dump_func):
            
            db = MyDB("mydatabase.db")

            assert db.fname == "mydatabase.db"

            mock_open_func.assert_not_called()
            mock_dump_func.assert_not_called()
    
    def describe_load_strings():
        def it_loads_an_array_from_a_file_and_returns_it_str(mock_load, mock_open_func):
            
            mock_load.return_value = ["5", "5we"]

            db = MyDB("mydatabase.db")
            assert db.fname == "mydatabase.db"
            result = db.loadStrings()

            mock_load.assert_called_once_with(mock_open_func())

            assert result == ["5", "5we"]
        def it_loads_an_array_from_a_file_and_returns_it_int(mock_load, mock_open_func):
            mock_load.return_value = [5, 1234]

            db = MyDB("mydatabase.db")
            assert db.fname == "mydatabase.db"
            result = db.loadStrings()

            mock_load.assert_called_once_with(mock_open_func())

            assert result == [5, 1234]

    def describe_save_strings():
        def it_saves_the_given_array_to_a_file(mock_dump_func, mock_open_func):
            db = MyDB("mydatabase.db")
            assert db.fname == "mydatabase.db"
            db.saveStrings(["use", "no"])

            assert mock_dump_func.call_count == 2
            assert mock_open_func.call_count == 2
        def it_writes_multiple_times(mock_dump_func, mock_open_func):
            db = MyDB("mydatabase.db")
            assert db.fname == "mydatabase.db"
            db.saveStrings(["use", "no"])
            db.saveStrings(["second", "save"])

            assert mock_dump_func.call_count == 3
            assert mock_open_func.call_count == 3
    
    def describe_save_string():
        def it_writes_string_element_to_existing_database(mock_dump_func, mock_open_func, mock_load):
            db = MyDB("mydatabase.db")
            assert db.fname == "mydatabase.db"
            db.saveString("Hello")

            assert mock_open_func.call_count == 3
            assert mock_load.call_count == 1
            assert mock_dump_func.call_count == 2