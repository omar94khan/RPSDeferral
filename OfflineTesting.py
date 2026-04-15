import json
import pandas as pd
from copy import deepcopy
from datetime import date
from dateutil.relativedelta import relativedelta

def DeferralRPS(
        FinanceAmount: float,
        ProfitRate: float,
        PayDay : int,
        DisbursementDate : str,
        TakafulFactor : float,
        EMI : float,
        GracePeriodMonths : int,
        repaymentMethod : str = "Deferral"
        ):
    
    DisbursementYear = int(DisbursementDate[0:4])
    DisbursementMonth = int(DisbursementDate[4:6])
    DisbursementDay = int(DisbursementDate[6:8])
    
    gracePeriodEndDate = date(DisbursementYear, DisbursementMonth, DisbursementDay) + relativedelta(months=GracePeriodMonths)
    
    if gracePeriodEndDate.day >= PayDay:
        FirstEMIYear = (gracePeriodEndDate + relativedelta(months=1)).year
        FirstEMIMonth = (gracePeriodEndDate + relativedelta(months=1)).month
    else:
        FirstEMIYear = gracePeriodEndDate.year
        FirstEMIMonth = gracePeriodEndDate.month
    
    if repaymentMethod == "Deferral":
        rps = {
            'SNo' : [],
            'Date' : [],
            'Days' : [],
            'EMI' : [],
            "GracePeriodProfitRecovery" : [],
            "GracePeriodTakafulRecovery" : [],
            'ProfitAmount' : [],
            'TakafulAmount' : [],
            'PrincipalAmount' : [],
            'OutstandingPrincipal' : []
           }

        distributionMonths = 1

        if GracePeriodMonths == 0:
            raise ValueError("Grace period cannot be 0 for Deferral method.")
        
        # Create the first row of the RPS to show the disbursement of the loan
        rps['SNo'].append(0)
        rps['Date'].append(date(DisbursementYear, DisbursementMonth, DisbursementDay))
        rps['Days'].append(0)
        rps['EMI'].append(0)
        rps['ProfitAmount'].append(0)
        rps['TakafulAmount'].append(0)
        rps['GracePeriodTakafulRecovery'].append(0)
        rps['GracePeriodProfitRecovery'].append(0)
        rps['PrincipalAmount'].append(0)
        rps['OutstandingPrincipal'].append(FinanceAmount)



        GracePeriodYear = gracePeriodEndDate.year
        GracePeriodMonth = gracePeriodEndDate.month
        GracePeriodDay = DisbursementDay

        # Create the second row of the RPS to show the end of the grace period
        rps['SNo'].append(1)
        rps['Date'].append(date(GracePeriodYear, GracePeriodMonth, GracePeriodDay))  
        rps['Days'].append((rps['Date'][-1] - rps['Date'][-2]).days)
        rps['EMI'].append(0)
        rps['ProfitAmount'].append(0)
        rps['TakafulAmount'].append(0)
        rps['GracePeriodTakafulRecovery'].append(0)
        rps['GracePeriodProfitRecovery'].append(0)
        rps['PrincipalAmount'].append(0)
        rps['OutstandingPrincipal'].append(rps['OutstandingPrincipal'][-1])


        # GracePeriodTakaful = rps['OutstandingPrincipal'][-1] * TakafulFactor * rps['Days'][-1] / 30
        GracePeriodTakaful = round(rps['OutstandingPrincipal'][-1] * TakafulFactor * GracePeriodMonths,3)
        GracePeriodProfit = round(rps['OutstandingPrincipal'][-1] * ProfitRate / 360 * rps['Days'][-1],3)


        # Calculate how many months will it take to pay off the Deferred Profit and Takaful amounts.
        while True:
            if distributionMonths > 360:
                raise ValueError("Installment too low to cater to deferrment with the given Profit and Takaful Rates.")


            rps_copy = deepcopy(rps)
            for i in range(0,distributionMonths):
                year = FirstEMIYear + ((FirstEMIMonth + (i-1))//12)
                month = ((FirstEMIMonth + (i-1)) % 12) + 1
                day = PayDay
                rps_copy['Date'].append(date(year, month, day))  
                rps_copy['Days'].append((rps_copy['Date'][-1] - rps_copy['Date'][-2]).days)
                rps_copy['ProfitAmount'].append(round(rps_copy['OutstandingPrincipal'][-1] * ProfitRate / 360 * rps_copy['Days'][-1],3))
                # rps_copy['TakafulAmount'].append(rps_copy['OutstandingPrincipal'][-1] * TakafulFactor * rps_copy['Days'][-1] / 30)
                rps_copy['TakafulAmount'].append(round(rps_copy['OutstandingPrincipal'][-1] * TakafulFactor,3))
                rps_copy['GracePeriodTakafulRecovery'].append(round(GracePeriodTakaful / distributionMonths,3))
                rps_copy['GracePeriodProfitRecovery'].append(round(GracePeriodProfit / distributionMonths,3))
                rps_copy['EMI'].append(EMI)
                rps_copy['PrincipalAmount'].append(round(rps_copy['EMI'][-1] - rps_copy['ProfitAmount'][-1] - rps_copy['TakafulAmount'][-1] - rps_copy['GracePeriodTakafulRecovery'][-1] - rps_copy['GracePeriodProfitRecovery'][-1],3))
                rps_copy['OutstandingPrincipal'].append(round(rps_copy['OutstandingPrincipal'][-1] - rps_copy['PrincipalAmount'][-1],3))

            if rps_copy['OutstandingPrincipal'][-1] < 0:
                EMI = rps_copy['EMI'][-1] + rps_copy['OutstandingPrincipal'][-1]
                PrincipalAmount = rps_copy['PrincipalAmount'][-1] + rps_copy['OutstandingPrincipal'][-1]
                rps_copy['EMI'][-1] = EMI
                rps_copy['PrincipalAmount'][-1] = PrincipalAmount
                rps_copy['OutstandingPrincipal'][-1] = 0
                break


            if sum(1 for i in rps_copy['PrincipalAmount'] if i < 0)== 0:
                break
            else:
                distributionMonths += 1

        # In case the loan is fully paid off during the distribution period, then we just copy the RPS without adding more rows to it. 
        if rps_copy['OutstandingPrincipal'][-1] > 0:
            
            # Add the rows for the period during which we are recovering the deferred profit and takaful amounts.
            for i in range (0, distributionMonths):
                rps['SNo'].append(2+i) 
                year = FirstEMIYear + ((FirstEMIMonth + (i-1))//12)
                month = ((FirstEMIMonth + (i-1)) % 12) + 1
                day = PayDay
                rps['Date'].append(date(year, month, day))  
                rps['Days'].append((rps['Date'][-1] - rps['Date'][-2]).days)
                rps['ProfitAmount'].append(round(rps['OutstandingPrincipal'][-1] * ProfitRate / 360 * rps['Days'][-1],3))
                # rps['TakafulAmount'].append(rps['OutstandingPrincipal'][-1] * TakafulFactor * rps['Days'][-1] / 30)
                rps['TakafulAmount'].append(round(rps['OutstandingPrincipal'][-1] * TakafulFactor,3))
                rps['GracePeriodTakafulRecovery'].append(round(GracePeriodTakaful / distributionMonths,3))
                rps['GracePeriodProfitRecovery'].append(round(GracePeriodProfit / distributionMonths,3))
                rps['EMI'].append(EMI)
                rps['PrincipalAmount'].append(round(max(0,rps['EMI'][-1] - rps['ProfitAmount'][-1] - rps['TakafulAmount'][-1] - rps['GracePeriodTakafulRecovery'][-1] - rps['GracePeriodProfitRecovery'][-1]),3))
                rps['OutstandingPrincipal'].append(round(rps['OutstandingPrincipal'][-1] - rps['PrincipalAmount'][-1],3))
                    

            i = distributionMonths

            while rps['OutstandingPrincipal'][-1] > 0:
                rps['SNo'].append(rps['SNo'][-1] + 1)
                year = FirstEMIYear + ((FirstEMIMonth + (i-1))//12)
                month = ((FirstEMIMonth + (i-1)) % 12) + 1
                day = PayDay
                rps['Date'].append(date(year, month, day))  
                
                rps['Days'].append((rps['Date'][-1] - rps['Date'][-2]).days)
                
                rps['EMI'].append(EMI)
                rps['ProfitAmount'].append(round(rps['OutstandingPrincipal'][-1] * ProfitRate / 360 * rps['Days'][-1],3))
                # rps['TakafulAmount'].append(rps['OutstandingPrincipal'][-1] * TakafulFactor * rps['Days'][-1] / 30)
                rps['TakafulAmount'].append(round(rps['OutstandingPrincipal'][-1] * TakafulFactor,3))
                rps['GracePeriodTakafulRecovery'].append(0)
                rps['GracePeriodProfitRecovery'].append(0)
                rps['PrincipalAmount'].append(round(max(0,rps['EMI'][-1] - rps['ProfitAmount'][-1] - rps['TakafulAmount'][-1] - rps['GracePeriodTakafulRecovery'][-1] - rps['GracePeriodProfitRecovery'][-1]),3))
                rps['OutstandingPrincipal'].append(round(rps['OutstandingPrincipal'][-1] - rps['PrincipalAmount'][-1],3))

                i += 1

            if rps['OutstandingPrincipal'][-1] < 0:
                EMI = rps['EMI'][-1] + rps['OutstandingPrincipal'][-1]
                PrincipalAmount = rps['PrincipalAmount'][-1] + rps['OutstandingPrincipal'][-1]
                rps['EMI'][-1] = EMI
                rps['PrincipalAmount'][-1] = PrincipalAmount
                rps['OutstandingPrincipal'][-1] = 0
                
        else:
            rps = rps_copy


    else:
        raise AttributeError("Please input the correct repaymentMethod. (Deferral)")
    
    df = pd.DataFrame(rps)

    return df