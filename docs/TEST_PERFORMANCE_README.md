# Tally Query Performance Test

## Overview
हे test file Tally queries ची performance measure करते वेगवेगळ्या date range strategies साठी.

## Test Strategies

### 1. **Full 6 Years - Single Query**
- Date Range: 01-04-2021 to 31-03-2026
- Strategy: एकच query (6 years)
- Expected: Slowest, but single query

### 2. **Per Financial Year**
- Date Range: 01-04-2021 to 31-03-2026
- Strategy: प्रत्येक financial year साठी separate query
- Expected: 6 queries (6 financial years)

### 3. **Per Month**
- Date Range: 01-04-2021 to 31-03-2026
- Strategy: प्रत्येक month साठी separate query
- Expected: ~72 queries (72 months)

### 4. **90 Days Chunks**
- Date Range: 01-04-2021 to 31-03-2026
- Strategy: 90-day chunks मध्ये divide
- Expected: ~24 queries

## Measurements

प्रत्येक query साठी measure होते:
- **Query Execution Time**: Tally query execute करण्यासाठी लागणारा वेळ
- **Fetch Time**: Results fetch करण्यासाठी लागणारा वेळ
- **Total Time**: Total time (Query + Fetch)
- **Rows Fetched**: किती rows fetch झाल्या
- **Batches**: किती batches मध्ये fetch झाल्या

## How to Run

### Method 1: Interactive Mode
```bash
python test_tally_query_performance.py
```

Script automatically:
1. DSN detect करेल (default: TallyODBC64_9000)
2. Companies list दाखवेल
3. Company select करण्यास सांगेल
4. सर्व tests run करेल
5. Results JSON file मध्ये save करेल

### Method 2: Direct Execution (Edit script)
Script मध्ये `main()` function edit करा:
```python
def main():
    dsn = "TallyODBC64_9000"  # Your DSN
    company_guid = "your-company-guid"  # From Tally
    company_name = "Your Company Name"
    
    run_performance_tests(dsn, company_guid, company_name)
```

## Output

### Console Output
```
📊 Testing: Full 6 Years - Single Query
   Query 1/1: 01-04-2021 to 31-03-2026... ✅ 125.5s (Query: 120.0s, Fetch: 5.5s, Rows: 50000)

📈 Summary:
   Total Time: 125.5s
   Query Time: 120.0s
   Fetch Time: 5.5s
   Total Rows: 50000
   Avg per Query: 125.5s
```

### JSON File Output
File name: `tally_performance_test_YYYYMMDD_HHMMSS.json`

```json
{
  "company_name": "Vrushali Infotech Pvt Ltd",
  "company_guid": "...",
  "test_date": "2025-12-16 12:30:00",
  "strategies": {
    "full_6_years": {
      "name": "Full 6 Years - Single Query",
      "total_queries": 1,
      "summary": {
        "total_time": 125.5,
        "total_query_execution_time": 120.0,
        "total_fetch_time": 5.5,
        "total_rows_fetched": 50000
      },
      "queries": [
        {
          "from_date": "01-04-2021",
          "to_date": "31-03-2026",
          "query_execution_time": 120.0,
          "fetch_time": 5.5,
          "total_time": 125.5,
          "rows_fetched": 50000
        }
      ]
    }
  }
}
```

## Performance Comparison

Test पूर्ण झाल्यावर comparison table दिसेल:

```
Strategy                        Total Time      Queries    Avg/Query      
----------------------------------------------------------------------
Full 6 Years - Single Query     125.50s         1          125.50s        
Per Financial Year              90.30s          6          15.05s         
Per Month                       85.20s           72         1.18s          
90 Days Chunks                  88.10s           24         3.67s          
```

## Expected Results

### Best Strategy (Expected)
- **Per Month**: Fastest average time per query
- **90 Days**: Good balance between speed and query count
- **Per Year**: Moderate speed
- **Full 6 Years**: Slowest (single large query)

### Why?
- Smaller date ranges = Faster queries
- More queries = Better progress tracking
- But more queries = More overhead

## Notes

1. **Time Measurements**:
   - Query Execution: Tally query execute करण्यासाठी लागणारा वेळ
   - Fetch Time: Results fetch करण्यासाठी लागणारा वेळ
   - Total: Query + Fetch

2. **Error Handling**:
   - Query fail झाल्यास error log होईल
   - Test continue होईल next query साठी

3. **Connection**:
   - प्रत्येक query साठी new connection
   - Real-world scenario simulate करण्यासाठी

4. **Batch Size**:
   - Default: 100 rows per batch
   - Script मध्ये change करू शकता

## Troubleshooting

### Connection Error
```
❌ Error getting companies: ...
```
**Solution**: DSN check करा, Tally running आहे का ते verify करा

### Query Timeout
```
❌ Error: Query execution timed out
```
**Solution**: Connection timeout increase करा (script मध्ये `timeout=60`)

### No Results
```
Rows: 0
```
**Solution**: Date range check करा, company GUID verify करा

## Next Steps

Test results नंतर:
1. Best strategy identify करा
2. App मध्ये implement करा
3. Auto-slicing logic optimize करा
4. User experience improve करा

