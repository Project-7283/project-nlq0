# Configuration Files

## sensitive_keywords.csv

This file defines keywords that identify sensitive columns in your database. When a column name contains any of these keywords, the DBProfilingService will automatically mask its data.

### Format
```csv
keyword,mask_type
password,full
token,full
```

### Fields
- `keyword`: The keyword to search for in column names (case-insensitive)
- `mask_type`: The masking strategy (currently only `full` is implemented)

### Default Keywords
The following keywords are included by default:
- `password` - User passwords
- `token` - API tokens, auth tokens
- `secret` - Secret keys, credentials
- `hash` - Password hashes
- `api_key` - API keys
- `private_key` - Private encryption keys
- `salt` - Password salts
- `ssn` - Social Security Numbers
- `credit_card` - Credit card information
- `cvv` - Card verification values
- `pin` - PIN codes
- `auth` - Authentication credentials
- `credential` - User credentials
- `key` - Generic key fields

### Customization

You can override this list by:

1. Editing this file directly
2. Creating your own CSV file and setting the environment variable:
   ```bash
   SENSITIVE_COLUMNS_CSV=path/to/your/keywords.csv
   ```

### How Masking Works

When a column name contains a sensitive keyword:

1. **Statistical Analysis**: Basic stats (distinct count, null %) are still computed
2. **Sample Data**: Replaced with `***MASKED***` in queries
3. **LLM Analysis**: Column is excluded from LLM analysis to prevent data leakage

#### Example

Column: `user_password_hash`
- Detected as sensitive (contains `password` and `hash`)
- Sample query becomes:
  ```sql
  SELECT 
    user_id,
    username,
    '***MASKED***' AS user_password_hash,
    email
  FROM users LIMIT 5
  ```
- LLM never sees the actual password hashes

### Disabling Masking

To disable all masking (not recommended for production):
```bash
DATA_MASKING_ENABLED=false
```
