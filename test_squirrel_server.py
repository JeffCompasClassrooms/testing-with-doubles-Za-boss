import io
import json
import pytest
import sqlite3
from squirrel_server import SquirrelServerHandler
from squirrel_db import SquirrelDB
from unittest.mock import call, patch, mock_open

# use @todo to cause pytest to skip that section
# handy for stubbing things out and then coming back later to finish them.
# @todo is heirarchical, and not sequential. Meaning that
# it will not skip 'peers' of other todos, only children.
todo = pytest.mark.skip(reason='TODO: pending spec')

class FakeRequest():
    def __init__(self, mock_wfile, method, path, body=None):
        self._mock_wfile = mock_wfile
        self._method = method
        self._path = path
        self._body = body

    def sendall(self, x):
        return

    #this is not a 'makefile' like in c++ instead it 'makes' a response file
    def makefile(self, *args, **kwargs):
        if args[0] == 'rb':
            if self._body:
                headers = 'Content-Length: {}\r\n'.format(len(self._body))
                body = self._body
            else:
                headers = ''
                body = ''
            request = bytes('{} {} HTTP/1.0\r\n{}\r\n{}'.format(self._method, self._path, headers, body), 'utf-8')
            return io.BytesIO(request)
        elif args[0] == 'wb':
            return self._mock_wfile

#dummy client and dummy server to pass as params
#when creating SquirrelServerHandler
@pytest.fixture
def dummy_client():
    return ('127.0.0.1', 80)

@pytest.fixture
def dummy_server():
    return None

#a patch for mocking the DB initialize 
# function - this gets called a lot.
@pytest.fixture
def mock_db_init(mocker):
    return mocker.patch.object(SquirrelDB, '__init__', return_value=None)

@pytest.fixture
def mock_db_get_squirrels(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrels', return_value=['squirrel'])


@pytest.fixture
def mock_db_get_squirrel(mocker, mock_db_init):
    return mocker.patch.object(SquirrelDB, 'getSquirrel', return_value='squirrel')

@pytest.fixture
def mock_db_create_squirrel():
    with patch("squirrel_db.SquirrelDB.createSquirrel", return_value=None) as m:
        yield m

@pytest.fixture
def mock_db_update_squirrel():
    with patch("squirrel_db.SquirrelDB.updateSquirrel", return_value=None) as m:
        yield m

@pytest.fixture
def mock_db_delete_squirrel():
    with patch("squirrel_db.SquirrelDB.deleteSquirrel", return_value=None) as m:
        yield m

@pytest.fixture
def mock_connect_sqlite3_db():
    with patch("sqlite3.connect") as mock_connect:
        yield mock_connect
        

# patch SquirrelServerHandler to make our FakeRequest work correctly
@pytest.fixture(autouse=True)
def patch_wbufsize(mocker):
    mocker.patch.object(SquirrelServerHandler, 'wbufsize', 1)
    mocker.patch.object(SquirrelServerHandler, 'end_headers')


# Fake Requests
@pytest.fixture
def fake_get_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/squirrels')

@pytest.fixture
def fake_get_squirrels_index_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/squirrels/1')

@pytest.fixture
def fake_bad_get_squirrels_index_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/squirrel/1')

@pytest.fixture
def fake_create_squirrel_request(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Chippy&size=small')

@pytest.fixture
def fake_bad_request_post(mocker):
    return FakeRequest(mocker.Mock(), 'POST', '/squirrels', body='name=Josh&')

@pytest.fixture
def fake_bad_get_request(mocker):
    return FakeRequest(mocker.Mock(), 'GET', '/squirrel')

@pytest.fixture
def fake_put_request(mocker):
    return FakeRequest(mocker.Mock(), 'PUT', '/squirrels/1', body="name=Fluffy&size=small")

@pytest.fixture
def fake_bad_put_request(mocker):
    return FakeRequest(mocker.Mock(), 'PUT', '/squirrel/1', body="name=Fluffy&size=small")

@pytest.fixture
def fake_delete_request(mocker):
    return FakeRequest(mocker.Mock(), 'DELETE', '/squirrels/1')

@pytest.fixture
def fake_bad_delete_request(mocker):
    return FakeRequest(mocker.Mock(), 'DELETE', '/squirrel/1')
#send_response, send_header and end_headers are inherited functions
#from the BaseHTTPRequestHandler. Go look at documentation here:
# https://docs.python.org/3/library/http.server.html
# Seriously. Go look at it. Pay close attention to what wfile is. :o)
# this fixture mocks all of the send____ that we use. 
# It is really just for convenience and cleanliness of code.
@pytest.fixture
def mock_response_methods(mocker):
    mock_send_response = mocker.patch.object(SquirrelServerHandler, 'send_response')
    mock_send_header = mocker.patch.object(SquirrelServerHandler, 'send_header')
    mock_end_headers = mocker.patch.object(SquirrelServerHandler, 'end_headers')
    return mock_send_response, mock_send_header, mock_end_headers


def describe_SquirrelServerHandler():
    def describe_index_squirrels_functionality():
        def it_returns_200_success_code(fake_get_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_db_create_squirrel, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            handler = SquirrelServerHandler(fake_get_request, dummy_client, dummy_server)

            assert mock_send_response.call_count == 1
            mock_send_response.assert_called_once_with(200)
        def it_queries_the_db_for_squirrels(fake_get_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_db_create_squirrel, mock_response_methods):
            handler = SquirrelServerHandler(fake_get_request, dummy_client, dummy_server)

            assert mock_db_get_squirrels.call_count == 1
        def it_sends_json_content_type_header(fake_get_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            SquirrelServerHandler(fake_get_request, dummy_client, dummy_server)
            
            mock_send_header.assert_called_once_with("Content-Type", "application/json")

        def it_calls_end_headers(fake_get_request, dummy_client, dummy_server, mock_db_get_squirrels, mock_response_methods):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            SquirrelServerHandler(fake_get_request, dummy_client, dummy_server)
            
            mock_end_headers.assert_called_once()
        
        def it_returns_response_body_with_squirrels_json_data(fake_get_request, dummy_client, dummy_server, mock_db_get_squirrels):
            response = SquirrelServerHandler(fake_get_request, dummy_client, dummy_server)

            response.wfile.write.assert_called_once_with(bytes(json.dumps(['squirrel']), "utf-8"))

    def describe_retrieve_squirrels_functionality():
        def it_returns_a_single_squirrel(fake_get_squirrels_index_request, dummy_client, dummy_server, mock_db_get_squirrel):
            handler = SquirrelServerHandler(fake_get_squirrels_index_request, dummy_client, dummy_server)
            
            mock_db_get_squirrel.assert_called_once_with('1')
            
            handler.wfile.write.assert_called_once_with(bytes(json.dumps("squirrel"), "utf-8"))

        def it_returns_200_on_good_request(fake_get_squirrels_index_request, dummy_client, dummy_server, mock_response_methods, mock_db_get_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            handler = SquirrelServerHandler(fake_get_squirrels_index_request, dummy_client, dummy_server)

            mock_send_response.assert_called_once_with(200)

        def it_returns_404_on_bad_request(fake_bad_get_squirrels_index_request, dummy_client, dummy_server, mock_response_methods, mock_db_get_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            handler = SquirrelServerHandler(fake_bad_get_squirrels_index_request, dummy_client, dummy_server)

            mock_send_response.assert_called_once_with(404)

        def it_sends_json_content_type(fake_get_squirrels_index_request, dummy_client, dummy_server, mock_response_methods, mock_db_get_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            handler = SquirrelServerHandler(fake_get_squirrels_index_request, dummy_client, dummy_server)

            mock_send_header.assert_called_once_with("Content-Type", "application/json")


    def describe_create_squirrels_functionality():
        def it_queries_db_to_create_squirrel_with_given_data_attributes(fake_create_squirrel_request, dummy_client, dummy_server, mock_response_methods, mock_db_create_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            handler = SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)

            mock_db_create_squirrel.assert_called_once_with("Chippy", "small")

        def it_returns_201_success_code(fake_create_squirrel_request, dummy_client, dummy_server, mock_response_methods, mock_db_create_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            handler = SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)

            mock_send_response.assert_called_once_with(201)
        def it_calls_end_headers(fake_create_squirrel_request, dummy_client, dummy_server, mock_response_methods, mock_db_create_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            handler = SquirrelServerHandler(fake_create_squirrel_request, dummy_client, dummy_server)

            assert mock_end_headers.call_count == 1
    def describe_update_squirrels_functionality():
        def it_writes_to_the_database(fake_put_request, dummy_client, dummy_server, mock_response_methods, mock_db_update_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            handler = SquirrelServerHandler(fake_put_request, dummy_client, dummy_server)

            mock_db_update_squirrel.assert_called_once_with('1', "Fluffy", "small")
        def it_returns_204_on_good_request(fake_put_request, dummy_client, dummy_server, mock_response_methods, mock_db_update_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            handler = SquirrelServerHandler(fake_put_request, dummy_client, dummy_server)

            mock_send_response.assert_called_once_with(204)

        def it_returns_404_on_bad_request(fake_bad_put_request, dummy_client, dummy_server, mock_response_methods, mock_db_update_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            handler = SquirrelServerHandler(fake_bad_put_request, dummy_client, dummy_server)

            mock_send_response.assert_called_once_with(404)
        def it_calls_end_headers(fake_put_request, dummy_client, dummy_server, mock_response_methods, mock_db_update_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods

            handler = SquirrelServerHandler(fake_put_request, dummy_client, dummy_server)

            assert mock_end_headers.call_count == 1
    def describe_delete_squirrels_functionality():

        def it_returns_204_on_good_request(fake_delete_request, dummy_client, dummy_server, mock_response_methods, mock_db_delete_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            handler = SquirrelServerHandler(fake_delete_request, dummy_client, dummy_server)

            mock_send_response.assert_called_once_with(204)

        def it_returns_404_on_bad_request(fake_bad_delete_request, dummy_client, dummy_server, mock_response_methods, mock_db_delete_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            handler = SquirrelServerHandler(fake_bad_delete_request, dummy_client, dummy_server)
            
            mock_send_response.assert_called_once_with(404)

        def it_calls_delete_squirrel(fake_delete_request, dummy_client, dummy_server, mock_response_methods, mock_db_delete_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            handler = SquirrelServerHandler(fake_delete_request, dummy_client, dummy_server)
            
            mock_db_delete_squirrel.assert_called_once_with('1')

        def it_calls_end_headers(fake_delete_request, dummy_client, dummy_server, mock_response_methods, mock_db_delete_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            handler = SquirrelServerHandler(fake_delete_request, dummy_client, dummy_server)
            
            assert mock_end_headers.call_count == 1
    def describe_handle404_functionality():
        def it_returns_404(fake_bad_get_request, dummy_client, dummy_server, mock_response_methods, mock_db_create_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            SquirrelServerHandler(fake_bad_get_request, dummy_client, dummy_server)
            
            assert mock_send_response.call_count == 1
            mock_send_response.assert_called_once_with(404)
        def it_sends_text_type(fake_bad_get_request, dummy_client, dummy_server, mock_response_methods, mock_db_create_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            SquirrelServerHandler(fake_bad_get_request, dummy_client, dummy_server)

            mock_send_header.assert_called_once_with("Content-Type", "text/plain")
        def it_writes_404_as_output(fake_bad_get_request, dummy_client, dummy_server, mock_response_methods, mock_db_create_squirrel):
            mock_send_response, mock_send_header, mock_end_headers = mock_response_methods
            
            response = SquirrelServerHandler(fake_bad_get_request, dummy_client, dummy_server)

            response.wfile.write.assert_called_once_with(bytes("404 Not Found", "utf-8"))

