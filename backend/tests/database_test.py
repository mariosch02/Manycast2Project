import pytest
from unittest.mock import MagicMock, patch
from db.db_factory import Database 
from mysql.connector import Error
from db.multithreading import *
@pytest.fixture
def db():
    """Fixture to initialize the Database class."""
    return Database()

@pytest.fixture
def mock_db():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    return mock_connection, mock_cursor

def test_connect_success(db):
    """Test successful database connection."""
    with patch('db.db_factory.mysql.connector.connect', return_value=MagicMock()) as mock_connect:
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True  
        mock_connect.return_value = mock_connection

        connection = db.connect()

        mock_connect.assert_called_once()

        assert connection is not None
        assert connection.is_connected()

def test_connect_failure(db):
    """Test database connection failure."""
    with patch('db.db_factory.mysql.connector.connect', side_effect=Error("Connection failed")):
        connection = db.connect()

        assert connection is None


def test_reconnect_existing_connection(db):
    """Test that connect() doesn't reconnect if the connection already exists and is connected."""
    mock_connection = MagicMock()
    mock_connection.is_connected.return_value = True
    db.connection = mock_connection

    connection = db.connect()

    mock_connection.is_connected.assert_called_once()
    assert connection == db.connection


def test_close_connection(db):
    """Test that the connection is properly closed."""
    mock_connection = MagicMock()
    db.connection = mock_connection

    db.close()

    mock_connection.close.assert_called_once()
    assert db.connection is not None


def test_close_no_connection(db):
    """Test closing the connection when there is no active connection."""
    db.connection = None

    db.close()

    assert db.connection is None


def test_initialize_database(db):
    """Test that the initialize_database() method runs the correct SQL queries."""
    mock_connect = MagicMock()
    mock_cursor = MagicMock()

    db.connection = mock_connect
    mock_connect.cursor.return_value = mock_cursor

    db.initialize_database()

    assert mock_cursor.execute.call_count > 0
    mock_connect.commit.assert_called_once()


def test_insert_new_ipid(db):
    """Test inserting a new IPID when it doesn't exist."""
    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.cursor.return_value = mock_cursor
    db.connection = mock_connection

    mock_cursor.fetchone.return_value = None
    mock_cursor.lastrowid = 10  

    new_ipid = db.get_or_insert_ipid('8.8.8.0/24', mock_cursor, db.connection)

    mock_cursor.execute.assert_any_call("SELECT IPID FROM IPAddresses WHERE Prefix = %s", ('8.8.8.0/24',))
    mock_cursor.execute.assert_any_call("INSERT INTO IPAddresses (Prefix) VALUES (%s)", ('8.8.8.0/24',))

    mock_connection.commit.assert_called_once()
    assert new_ipid == 10



def test_get_existing_ipid(db):
    """Test retrieving an existing IPID."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (5,)  

    existing_ipid = db.get_or_insert_ipid('8.8.8.0/24', mock_cursor, db.connection)

    mock_cursor.execute.assert_called_once_with("SELECT IPID FROM IPAddresses WHERE Prefix = %s", ('8.8.8.0/24',))

    assert existing_ipid == 5

def test_disable_foreign_key_checks(db):
    """Test that foreign key checks are disabled."""
    mock_cursor = MagicMock()
    db.connection = MagicMock()
    db.connection.cursor.return_value = mock_cursor

    db.disable_foreign_key_checks()

    mock_cursor.execute.assert_called_once_with("SET foreign_key_checks = 0;")


def test_enable_foreign_key_checks(db):
    """Test that foreign key checks are enabled."""
    mock_cursor = MagicMock()
    db.connection = MagicMock()
    db.connection.cursor.return_value = mock_cursor

    db.enable_foreign_key_checks()

    mock_cursor.execute.assert_called_once_with("SET foreign_key_checks = 1;")




def test_get_or_insert_ipid_found(mock_db):
    connection, cursor = mock_db
    ip_cache = {}

    cursor.fetchone.return_value = {'IPID': 123}

    ipid = get_or_insert_ipid('8.8.8.0/24', cursor, connection, ip_cache)

    cursor.execute.assert_called_with("SELECT IPID FROM IPAddresses WHERE Prefix = %s", ('8.8.8.0/24',))
    assert ipid == 123
    assert '8.8.8.0/24' in ip_cache
    assert ip_cache['8.8.8.0/24'] == 123


def test_get_or_insert_ipid_not_found(mock_db):
    connection, cursor = mock_db
    ip_cache = {}

    cursor.fetchone.side_effect = [None, {'IPID': 456}]  

    ipid = get_or_insert_ipid('1.1.1.0/24', cursor, connection, ip_cache)
    cursor.execute.assert_any_call("SELECT IPID FROM IPAddresses WHERE Prefix = %s", ('1.1.1.0/24',))
    cursor.execute.assert_any_call("INSERT IGNORE INTO IPAddresses (Prefix) VALUES (%s)", ('1.1.1.0/24',))
    connection.commit.assert_called_once()
    assert ipid == 456
    assert '1.1.1.0/24' in ip_cache
    assert ip_cache['1.1.1.0/24'] == 456


def test_insert_data_v4_success(mock_db):
    connection, cursor = mock_db

    json_data = [
        {
            "prefix": "8.8.8.0/24",
            "characterization": {
                "MAnycastICMPv4": {"anycast": "yes", "instances": 1},
                "MAnycastTCPv4": {"anycast": "yes", "instances": 2},
                "MAnycastUDPv4": {"anycast": "yes", "instances": 3},
                "iGreedyICMPv4": {"anycast": "no", "instances": 4},
                "iGreedyTCPv4": {"anycast": "no", "instances": 5}
            }
        }
    ]

    cursor.fetchone.side_effect = [{'IPID': 123}]  # Simulate an IPID being returned

    insert_data_v4(json_data, '2024-03-21', cursor, connection)

    cursor.executemany.assert_called_once()
    connection.commit.assert_called_once()

def test_insert_data_v4_error(mock_db):
    connection, cursor = mock_db

    json_data = [
        {
            "prefix": "8.8.8.0/24",
            "characterization": {
                "MAnycastICMPv4": {"anycast": "yes", "instances": 1},
                "MAnycastTCPv4": {"anycast": "yes", "instances": 2},
                "MAnycastUDPv4": {"anycast": "yes", "instances": 3},
                "iGreedyICMPv4": {"anycast": "no", "instances": 4},
                "iGreedyTCPv4": {"anycast": "no", "instances": 5}
            }
        }
    ]

    cursor.executemany.side_effect = Exception('Database insert error')

    with pytest.raises(Exception, match='Database insert error'):
        insert_data_v4(json_data, '2024-03-21', cursor, connection)

    connection.commit.assert_not_called()



def test_insert_data_v6_error(mock_db):
    connection, cursor = mock_db

    json_data = [
        {
            "prefix": "2001:4860:4860::8888/32",
            "characterization": {
                "MAnycastICMPv6": {"anycast": "yes", "instances": 1},
                "MAnycastTCPv6": {"anycast": "yes", "instances": 2},
                "MAnycastUDPv6": {"anycast": "yes", "instances": 3},
                "iGreedyICMPv6": {"anycast": "no", "instances": 4},
                "iGreedyTCPv6": {"anycast": "no", "instances": 5}
            }
        }
    ]

    cursor.executemany.side_effect = Exception('Database insert error')

    with pytest.raises(Exception, match='Database insert error'):
        insert_data_v6(json_data, '2024-03-21', cursor, connection)

    connection.commit.assert_not_called()


def test_insert_data_v6_empty(mock_db):
    connection, cursor = mock_db

    json_data = []

    insert_data_v6(json_data, '2024-03-21', cursor, connection)

    cursor.executemany.assert_not_called()
    connection.commit.assert_not_called()


