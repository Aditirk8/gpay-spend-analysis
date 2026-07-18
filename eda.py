import duckdb

con=duckdb.connect("data/gpay.duckdb")

#Checking for missing values 
print("Null Counts")
print(con.execute("""
                  SELECT
                  COUNT(*) - COUNT(date) as missing_data,
                  COUNT(*) - COUNT(merchant) as missing_merchant,
                  COUNT(*) - COUNT(amount) as missing_amount
                  FROM transactions
                  """).df())

#Checking for outliers 
print("Amount statistics")
print(con.execute("""
                  SELECT MIN(amount), MAX(amount), ROUND(AVG(amount), 2) as avg
                  FROM transactions
                  """).df())

#Checking for zero or negative amounts 
print("Zero or negative amounts")
print(con.execute("""
                  SELECT COUNT(*) as count 
                  FROM transactions 
                  WHERE amount<=0
                  """).df())

#Date range
print("Date range")
print(con.execute("""
                 SELECT MIN(date) as earliest, MAX(date) as latest 
                  FROM transactions
                  """).df())

#Calculating transactions per month 
print("Transactions per month")
print(con.execute("""
                  SELECT month, COUNT(*) as txns, ROUND(SUM(amount), 2) as total
                  FROM transactions
                  GROUP BY month
                  ORDER BY month
                  """).df())

con.close()
