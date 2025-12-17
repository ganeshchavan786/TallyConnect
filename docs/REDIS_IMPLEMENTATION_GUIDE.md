# Redis Implementation Guide for TallyConnect

## 📋 Overview

Redis (Remote Dictionary Server) हा in-memory data structure store आहे जो caching, session management, आणि real-time features साठी वापरला जातो.

---

## 🎯 Redis Use Cases for TallyConnect

### 1. Query Result Caching ⭐ **PRIMARY USE**

**Benefits**:
- Dashboard queries 10x faster
- Reduced database load
- Better user experience

**What to Cache**:
- Company list
- Dashboard data (by company + FY)
- Report data
- Ledger summaries

**Example**:
```python
# Cache dashboard data
cache_key = f"dashboard:{guid}:{alterid}:{fy}"
data = redis.get(cache_key)
if not data:
    data = calculate_dashboard()  # Expensive operation
    redis.set(cache_key, data, ttl=300)  # 5 minutes
```

---

### 2. Session Management (Future)

**If multi-user support added**:
- User sessions
- Authentication tokens
- Active user tracking

---

### 3. Real-time Features (Future)

**Pub/Sub for**:
- Sync progress updates
- Live dashboard updates
- Notifications

---

### 4. Rate Limiting

**API protection**:
- Request throttling
- Abuse prevention

---

## 🚀 Implementation

### Step 1: Install Redis

**Windows Options**:

**Option A: Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**Option B: WSL (Windows Subsystem for Linux)**
```bash
wsl
sudo apt-get update
sudo apt-get install redis-server
redis-server
```

**Option C: Memurai (Windows Native)**
- Download from: https://www.memurai.com/
- Install and run as service

### Step 2: Install Python Client

```bash
pip install redis
```

### Step 3: Configuration

**Update `.env` file**:
```env
# Redis Configuration
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_DEFAULT_TTL=300
```

**Update `backend/config/settings.py`**:
```python
# Redis Configuration
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DEFAULT_TTL = int(os.getenv("REDIS_DEFAULT_TTL", "300"))
```

### Step 4: Create Redis Cache Utility

**File: `backend/utils/redis_cache.py`**
```python
"""
Redis Cache Utility
===================

Handles caching operations using Redis.
"""

import redis
import json
from typing import Optional, Any
from backend.config.settings import (
    REDIS_ENABLED, REDIS_HOST, REDIS_PORT, 
    REDIS_DB, REDIS_PASSWORD, REDIS_DEFAULT_TTL
)


class RedisCache:
    """Redis cache wrapper with fallback to in-memory cache."""
    
    def __init__(self):
        self.enabled = REDIS_ENABLED
        self.client = None
        self.fallback_cache = {}  # In-memory fallback
        
        if self.enabled:
            try:
                self.client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self.client.ping()
                print("✅ Redis connected successfully")
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}. Using in-memory cache.")
                self.enabled = False
                self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.enabled and self.client:
            try:
                value = self.client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"⚠️ Redis get error: {e}")
                return None
        
        # Fallback to in-memory
        return self.fallback_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache with TTL (seconds)."""
        if ttl is None:
            ttl = REDIS_DEFAULT_TTL
        
        if self.enabled and self.client:
            try:
                self.client.setex(key, ttl, json.dumps(value))
            except Exception as e:
                print(f"⚠️ Redis set error: {e}")
                # Fallback to in-memory
                self.fallback_cache[key] = value
        else:
            # In-memory cache (no TTL support)
            self.fallback_cache[key] = value
    
    def delete(self, key: str):
        """Delete key from cache."""
        if self.enabled and self.client:
            try:
                self.client.delete(key)
            except Exception as e:
                print(f"⚠️ Redis delete error: {e}")
        
        # Also remove from fallback
        self.fallback_cache.pop(key, None)
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self.enabled and self.client:
            try:
                return self.client.exists(key) > 0
            except:
                return False
        return key in self.fallback_cache
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        if self.enabled and self.client:
            try:
                for key in self.client.scan_iter(match=pattern):
                    self.client.delete(key)
            except Exception as e:
                print(f"⚠️ Redis clear_pattern error: {e}")
        
        # Clear from fallback
        keys_to_remove = [k for k in self.fallback_cache.keys() if pattern.replace('*', '') in k]
        for key in keys_to_remove:
            del self.fallback_cache[key]
    
    def clear_all(self):
        """Clear all cache."""
        if self.enabled and self.client:
            try:
                self.client.flushdb()
            except Exception as e:
                print(f"⚠️ Redis clear_all error: {e}")
        
        self.fallback_cache.clear()


# Global cache instance
_cache_instance = None

def get_cache() -> RedisCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
```

### Step 5: Use Cache in Code

**Example: Cache Dashboard Data**

```python
# backend/database/queries.py or portal_server.py
from backend.utils.redis_cache import get_cache

def get_dashboard_data(guid, alterid, fy):
    cache = get_cache()
    cache_key = f"dashboard:{guid}:{alterid}:{fy}"
    
    # Try cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Calculate if not in cache
    data = calculate_dashboard_data(guid, alterid, fy)
    
    # Store in cache
    cache.set(cache_key, data, ttl=300)  # 5 minutes
    
    return data
```

**Example: Cache Company List**

```python
# backend/database/company_dao.py
from backend.utils.redis_cache import get_cache

def get_all_synced(self) -> List[Tuple]:
    cache = get_cache()
    cache_key = "companies:all:synced"
    
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    query = "SELECT name, alterid, status, total_records, guid FROM companies WHERE status='synced' ORDER BY name"
    cur = self._execute(query)
    result = cur.fetchall()
    
    # Cache for 10 minutes
    cache.set(cache_key, result, ttl=600)
    
    return result
```

---

## 📊 Performance Benefits

### Without Redis:
- Dashboard query: 2-5 seconds
- Company list: 0.5-1 second
- Report generation: 5-10 seconds

### With Redis:
- Dashboard query: 0.1-0.5 seconds (cached)
- Company list: 0.01-0.1 seconds (cached)
- Report generation: 0.5-2 seconds (cached)

**Improvement**: **5-10x faster** for cached queries

---

## 🔧 Configuration Options

### Development (Local)
```env
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Production
```env
REDIS_ENABLED=true
REDIS_HOST=redis-server.example.com
REDIS_PORT=6379
REDIS_PASSWORD=secure_password
REDIS_DEFAULT_TTL=600
```

### Disable Redis (Fallback)
```env
REDIS_ENABLED=false
```
- Automatically uses in-memory cache
- No Redis dependency

---

## 🎯 Cache Keys Strategy

### Naming Convention
```
{resource}:{identifier}:{filter}
```

### Examples
```
companies:all:synced
dashboard:{guid}:{alterid}:{fy}
ledger:{guid}:{alterid}:{ledger_name}:{from_date}:{to_date}
outstanding:{guid}:{alterid}:{as_on_date}
```

### TTL (Time To Live)
- **Company list**: 10 minutes (600s)
- **Dashboard data**: 5 minutes (300s)
- **Report data**: 15 minutes (900s)
- **Ledger data**: 10 minutes (600s)

---

## 🧪 Testing

### Test Redis Connection
```python
from backend.utils.redis_cache import get_cache

cache = get_cache()
if cache.enabled:
    print("✅ Redis is enabled and connected")
else:
    print("⚠️ Redis disabled, using in-memory cache")
```

### Test Cache Operations
```python
cache = get_cache()

# Set
cache.set("test:key", {"data": "value"}, ttl=60)

# Get
data = cache.get("test:key")
print(data)  # {'data': 'value'}

# Delete
cache.delete("test:key")
```

---

## ⚠️ Important Notes

### 1. Cache Invalidation
- Clear cache when data changes
- Example: After sync, clear dashboard cache

```python
# After sync completes
cache = get_cache()
cache.clear_pattern(f"dashboard:{guid}:{alterid}:*")
```

### 2. Memory Management
- Redis uses RAM
- Monitor memory usage
- Set appropriate TTL values

### 3. Fallback Strategy
- Code automatically falls back to in-memory cache
- No breaking changes if Redis unavailable

### 4. Data Serialization
- All data is JSON serialized
- Complex objects must be JSON-serializable

---

## 📈 Monitoring

### Redis CLI Commands
```bash
# Connect to Redis
redis-cli

# Check memory usage
INFO memory

# List all keys
KEYS *

# Get key value
GET dashboard:guid:alterid:fy

# Check TTL
TTL dashboard:guid:alterid:fy
```

---

## ✅ Summary

### Benefits:
- ✅ **5-10x faster** queries (cached)
- ✅ **Reduced database load**
- ✅ **Better scalability**
- ✅ **Real-time features** (future)

### Implementation:
- ✅ **Optional** - Works without Redis (fallback)
- ✅ **Easy setup** - Docker or WSL
- ✅ **Flexible** - Enable/disable via config

### Priority:
- 🟡 **HIGH** - Significant performance improvement

---

**Last Updated**: December 2025

