import pytest
import time
from unittest.mock import Mock, patch
from app.services.cache_service import CacheService

@pytest.fixture
def mock_redis():
    with patch('app.services.cache_service.Redis') as mock:
        yield mock

@pytest.fixture
def cache_service(mock_redis):
    return CacheService()

def test_get_cache_hit(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.get.return_value = '{"key": "value"}'
    
    # Test
    result = cache_service.get('test_key')
    
    # Assert
    assert result == {'key': 'value'}
    mock_redis.return_value.get.assert_called_once_with('test_key')

def test_get_cache_miss(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.get.return_value = None
    
    # Test
    result = cache_service.get('test_key')
    
    # Assert
    assert result is None
    mock_redis.return_value.get.assert_called_once_with('test_key')

def test_set_cache(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.setex.return_value = True
    
    # Test
    result = cache_service.set('test_key', {'key': 'value'}, ttl=3600)
    
    # Assert
    assert result is True
    mock_redis.return_value.setex.assert_called_once()
    call_args = mock_redis.return_value.setex.call_args[0]
    assert call_args[0] == 'test_key'
    assert call_args[1] == 3600
    assert call_args[2] == '{"key": "value"}'

def test_delete_cache(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.delete.return_value = 1
    
    # Test
    result = cache_service.delete('test_key')
    
    # Assert
    assert result is True
    mock_redis.return_value.delete.assert_called_once_with('test_key')

def test_get_many_cache(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.mget.return_value = [
        '{"key1": "value1"}',
        '{"key2": "value2"}',
        None
    ]
    
    # Test
    result = cache_service.get_many(['key1', 'key2', 'key3'])
    
    # Assert
    assert result == {
        'key1': {'key1': 'value1'},
        'key2': {'key2': 'value2'}
    }
    mock_redis.return_value.mget.assert_called_once_with(['key1', 'key2', 'key3'])

def test_set_many_cache(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.pipeline.return_value.execute.return_value = [True, True]
    
    # Test
    result = cache_service.set_many({
        'key1': {'value1': 'data1'},
        'key2': {'value2': 'data2'}
    }, ttl=3600)
    
    # Assert
    assert result is True
    pipeline = mock_redis.return_value.pipeline.return_value
    assert pipeline.setex.call_count == 2

def test_delete_many_cache(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.delete.return_value = 2
    
    # Test
    result = cache_service.delete_many(['key1', 'key2'])
    
    # Assert
    assert result is True
    mock_redis.return_value.delete.assert_called_once_with('key1', 'key2')

def test_clear_cache(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.flushdb.return_value = True
    
    # Test
    result = cache_service.clear()
    
    # Assert
    assert result is True
    mock_redis.return_value.flushdb.assert_called_once()

def test_get_stats(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.info.return_value = {
        'used_memory': 1000,
        'used_memory_peak': 2000,
        'connected_clients': 1,
        'db0': {'keys': 10},
        'keyspace_hits': 100,
        'keyspace_misses': 50
    }
    
    # Test
    result = cache_service.get_stats()
    
    # Assert
    assert result == {
        'used_memory': 1000,
        'used_memory_peak': 2000,
        'connected_clients': 1,
        'total_keys': 10,
        'hits': 100,
        'misses': 50
    }
    mock_redis.return_value.info.assert_called_once()

def test_error_handling(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.get.side_effect = Exception('Redis error')
    
    # Test
    result = cache_service.get('test_key')
    
    # Assert
    assert result is None

def test_performance_monitoring(cache_service, mock_redis):
    # Setup
    mock_redis.return_value.get.return_value = '{"key": "value"}'
    
    # Test
    start_time = time.time()
    result = cache_service.get('test_key')
    duration = time.time() - start_time
    
    # Assert
    assert result == {'key': 'value'}
    assert duration < 0.1  # Should be very fast 