import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3

df = pd.read_csv("loan_data_set.csv")
df['Loan_Amount'].fillna(df['Loan_Amount'].median(), inplace=True)
df['Credit_History'].fillna(0, inplace=True)

conn = sqlite3.connect(':memory:')
df.to_sql('loan_data', conn, index=False,if_exists='replace')

#INCOMES
# for those with loan approvals
conn.execute("ALTER TABLE loan_data ADD total_income INT")
conn.execute("""
            UPDATE loan_data
            SET total_income = ApplicantIncome + CoapplicantIncome
             """)

query = """SELECT Loan_Status, avg(total_income) AS average_income
        FROM loan_data 
        GROUP by Loan_Status
"""
incomes = pd.read_sql_query(query, conn)
print(incomes)

# AVERAGE LOAN AMOUNTS
query1 = ("""SELECT Loan_Status, avg(Loan_Amount) AS avg_loan_amount
            FROM loan_data 
            GROUP BY Loan_Status
          """)
average_loans = pd.read_sql_query(query1, conn)
print(f"Average loan amounts:",average_loans)

# Loan Approval Rate
query2 = "SELECT COUNT(*) FROM loan_data WHERE Loan_Status= 'Y'"
query3 = "SELECT COUNT(*) FROM loan_data"
loans_approved = pd.read_sql_query(query2, conn)
loans_applied = pd.read_sql_query(query3, conn)
print(f"Loan Approval Rate: {loans_approved*100/loans_applied}")

# Income to Loan Ratio
conn.execute("ALTER TABLE loan_data ADD income_loan_ratio DEC(4, 2)")
conn.execute("""UPDATE loan_data
             SET income_loan_ratio = total_income/Loan_Amount
             """)
query4 = """SELECT Loan_Status, avg(income_loan_ratio) AS avg_il_ratio
        FROM loan_data 
        GROUP by Loan_Status
"""
il_ratio = pd.read_sql_query(query4, conn)
print(il_ratio)

# Approval Rate by Gender
query5 = ("SELECT COUNT(*) FROM loan_data WHERE Gender = 'Male' and Loan_Status = 'Y'")
query6 = ("SELECT COUNT(*) FROM loan_data WHERE Gender = 'Male'")
query7 = ("SELECT COUNT(*) FROM loan_data WHERE Gender = 'Female' and Loan_Status = 'Y'")
query8 = ("SELECT COUNT(*) FROM loan_data WHERE Gender = 'Female'")
male_approved = pd.read_sql_query(query5, conn)
female_approved = pd.read_sql_query(query7, conn)
males = pd.read_sql_query(query6, conn)
females = pd.read_sql_query(query8, conn)
print(f"Male Approval Rate: {male_approved*100/males}")
print(f"Female Approval Rate: {female_approved*100/females}")

# Approval Rate by Education
query9 = ("SELECT COUNT(*) FROM loan_data WHERE Education = 'Graduate' and Loan_Status = 'Y'")
education_approved = pd.read_sql_query(query9, conn)
print(f"Education Approval Rate: {education_approved*100/loans_applied}")

# Approval Rate by Credit History
query10 = ("SELECT COUNT(*) FROM loan_data WHERE Credit_History = '1' and Loan_Status = 'Y'")
credit_history_approved = pd.read_sql_query(query10, conn)
print(f"Credit History Approval Rate: {credit_history_approved*100/loans_applied}")