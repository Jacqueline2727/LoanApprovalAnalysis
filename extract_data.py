import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3

df = pd.read_csv("loan_data_set.csv")
df['Loan_Amount'] = df['Loan_Amount'].fillna(df['Loan_Amount'].median())
df['Credit_History'] = df['Credit_History'].fillna(0)

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
incomes_list = pd.read_sql_query(query, conn)['average_income'].tolist()
print(f"Average income list: {incomes_list}")

# AVERAGE LOAN AMOUNTS
query1 = ("""SELECT Loan_Status, avg(Loan_Amount) AS avg_loan_amount
            FROM loan_data 
            GROUP BY Loan_Status
          """)
average_loans = pd.read_sql_query(query1, conn)
print(average_loans)
average_loan_list = pd.read_sql_query(query1, conn)['avg_loan_amount'].tolist()
print(f"Average loan amounts:",average_loan_list)

# Loan Approval Rate
query2 = "SELECT COUNT(*) AS approved_count FROM loan_data WHERE Loan_Status= 'Y'"
query3 = "SELECT COUNT(*) AS nonapproved_count FROM loan_data"
loans_approved = pd.read_sql_query(query2, conn)['approved_count'].iloc[0]
loans_applied = pd.read_sql_query(query3, conn)['nonapproved_count'].iloc[0]
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
il_ratio = pd.read_sql_query(query4, conn)['avg_il_ratio'].tolist()
print(f"Income to Loan Ratio: {il_ratio}")

# Approval Rate by Gender
query5 = ("SELECT COUNT(*) AS male_approved FROM loan_data WHERE Gender = 'Male' and Loan_Status = 'Y'")
query6 = ("SELECT COUNT(*) AS male FROM loan_data WHERE Gender = 'Male'")
query7 = ("SELECT COUNT(*) AS female_approved FROM loan_data WHERE Gender = 'Female' and Loan_Status = 'Y'")
query8 = ("SELECT COUNT(*) AS female FROM loan_data WHERE Gender = 'Female'")
male_ratio = pd.read_sql_query(query5, conn)['male_approved'].iloc[0]*100/pd.read_sql_query(query6, conn)['male'].iloc[0]
female_ratio = pd.read_sql_query(query7, conn)['female_approved'].iloc[0]*100/pd.read_sql_query(query8, conn)['female'].iloc[0]
gender_rates = [male_ratio, female_ratio]
print(f"Gender Approval Rates: {gender_rates}")

# Approval Rate by Education
query9 = ("SELECT COUNT(*) AS education_count FROM loan_data WHERE Education = 'Graduate' and Loan_Status = 'Y'")
education_approved = pd.read_sql_query(query9, conn)['education_count'].iloc[0]
education_rate = [education_approved*100/loans_applied, 100-(education_approved*100/loans_applied)]
print(f"Education Approval Rate: {education_rate}")

# Approval Rate by Credit History
query10 = ("SELECT COUNT(*) AS credit_hist_count FROM loan_data WHERE Credit_History = '1' and Loan_Status = 'Y'")
credit_history_approved = pd.read_sql_query(query10, conn)['credit_hist_count'].iloc[0]
credit_history_rate = [credit_history_approved*100/loans_applied, 100-(credit_history_approved*100/loans_applied)]
print(f"Credit History Approval Rate: {credit_history_rate}")

# Visualization
data = {'Male':male_ratio, 'Female':female_ratio,
        'Graduate': education_rate[0], 'Non-Graduate':education_rate[1],
        'Has Credit History':credit_history_rate[0], 'No Credit History':credit_history_rate[1]}

group_data = list(data.values())
group_names = list(data.keys())

fig, ax = plt.subplots()
ax.bar(group_names, group_data)
ax.set_xlabel('Attributes')
ax.set_ylabel('Loan Approval Rate')
ax.set_title('Loan Approval Rate vs Client Attributes')

plt.show()
