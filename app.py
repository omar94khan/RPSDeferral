import streamlit as st
import OfflineTesting
from datetime import date

def is_difference_valid(disbursement_date, PayDay):
    # If the PayDay has already passed this month, calculate for the next month
    if PayDay <= disbursement_date.day:
        # Handle the case for December by rolling over to January of the next year
        if disbursement_date.month == 12:
            PayDay_date = date(disbursement_date.year + 1, 1, PayDay)
        else:
            PayDay_date = date(disbursement_date.year, disbursement_date.month + 1, PayDay)
    
    else:
        PayDay_date = date(disbursement_date.year, disbursement_date.month, PayDay)
    # Calculate the difference in days
    difference = (PayDay_date - disbursement_date).days
    
    # Check if the difference is at least 5 days
    return difference <= 5


def main():
    st.title('Repayment Schedule Generator')

    st.write('Please input the factors for the Finance deal and click on the Generate button to display the Repayment Schedule.')
    
    
    FinanceAmount = st.number_input(label = "Please input the Finance Amount", min_value = 0.001, format="%0.3f", step = 0.001, value = 5000.000)
    ProfitRate = (st.number_input(label = "Please input the annual Profit Rate in Percentage terms", min_value = 0.00, format="%0.2f", value = 5.0))/100
    payday = st.number_input(label = "Please define the date for monthly EMI payments", min_value = 1, max_value = 28, value = 1, step = 1)
    disbursement_date = st.date_input(label = "Please define the Disbursement Date.", value = None)
    disbursement_date_string = str(disbursement_date).replace("-","")   
    EMI = st.number_input(label = "Please input the EMI", min_value = 0.001, format="%0.3f", step = 0.001, value = 100.000)
    TakafulFactor = (st.number_input(label = "Please input the Takaful Rate in Monthly Percentage terms", min_value = 0.00, format="%0.2f", value = 5.5))/100
    GracePeriodMonths = st.number_input(label = "Please input the Grace Period in months", min_value = 0, max_value = 36, value = 3, step = 1)


    

    
    def generate_rps():
        df_final = OfflineTesting.DeferralRPS(FinanceAmount = FinanceAmount,
                                              ProfitRate = ProfitRate,
                                              PayDay = payday,
                                              DisbursementDate = disbursement_date_string,
                                              EMI = EMI,
                                              TakafulFactor = TakafulFactor,
                                              GracePeriodMonths = GracePeriodMonths,
                                              repaymentMethod = "Deferral").set_index("SNo")

        st.write(df_final)
        st.write(df_final.iloc[:,3:-1].sum())

    generate = st.button(label = "Generate Repayment Schedule", on_click = generate_rps)



    # st.write(alsalamfinance.goalSeek().set_index('SNo'))

main()