# Redis Setup - Quick Guide

## Sales Register Performance Issue Fix

Sales Register hang होत होते कारण 1439 vouchers process करण्यासाठी खूप वेळ लागत होता.

**Solution:** Redis caching जोडले आहे. आता:
- **First Request:** Database query (slow)
- **Next Requests:** Redis cache (10-50x faster!)

---

## Redis Enable करणे

### Option 1: Redis Server Install करा (Recommended)

**Windows:**
1. Download Redis: https://github.com/microsoftarchive/redis/releases
2. Install Redis
3. Start Redis service

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### Option 2: In-Memory Cache (Default - Already Working)

Redis install न करता देखील काम करेल - in-memory cache automatically use होईल.

---

## Configuration

### Step 1: `.env` file update करा

```env
# Redis Cache Configuration
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
CACHE_TTL_SECONDS=3600
```

### Step 2: Redis Python package install करा

```bash
pip install redis>=5.0.0
```

### Step 3: Server restart करा

```bash
python main.py
```

---

## Performance Improvement

### Before (Without Cache):
- **First Request:** ~30-60 seconds (1439 vouchers process)
- **Every Request:** Same 30-60 seconds

### After (With Redis Cache):
- **First Request:** ~30-60 seconds (cache miss - process data)
- **Next Requests:** ~0.5-2 seconds (cache hit - instant!)

**Improvement:** **10-50x faster!**

---

## Cache TTL (Time To Live)

- **Monthly Summary:** 1 hour (3600 seconds)
- **Voucher List:** 30 minutes (1800 seconds)

Cache automatically expire होईल आणि fresh data load होईल.

---

## Cache Invalidation

Cache automatically invalidate होईल जेव्हा:
- Company sync complete होईल
- New data sync होईल

---

## Troubleshooting

### Redis connection failed?
- Check Redis server running: `redis-cli ping` (should return `PONG`)
- Check `.env` file: `REDIS_ENABLED=true
- Check firewall/port: Port 6379 should be open

### Still using in-memory cache?
- Check logs: `[CACHE] Redis not installed, using in-memory cache`
- Install Redis server or install `redis` package: `pip install redis`

---

## Status Check

Server logs मध्ये दिसेल:
- `[CACHE] Redis connected successfully` - Redis working
- `[CACHE] Redis not installed, using in-memory cache` - In-memory cache (also fast!)
- `[INFO] Sales Register: Cache HIT` - Cache working (fast!)
- `[INFO] Sales Register: Cache MISS` - First request (slow, but caches result)

---

**Note:** In-memory cache देखील fast आहे, पण Redis better आहे distributed systems साठी.

