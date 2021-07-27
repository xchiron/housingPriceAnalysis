import numpy as np
import pandas as pd

class housingInvestment(object):
    def __init__ (self, address, purchasePrice, annualTax, interestRate, yearsTillPayoff, chargedRent=0, vacancy=0.05, repairs=0.08, avgCapX=0.05, HOA=0, mngFee = 0.1, water = 0, electric = 0, trash = 20, gas = 0, internet = 0, insurance = 0, calcUtilities = False):
        #Known Values
        self.purchasePrice = purchasePrice
        self.address = address
        self.annualTax = annualTax
        self.avgVacancy = vacancy
        self.calcUtilities = calcUtilities
        self.avgCapitalExpenditures = avgCapX #new roof, heating, etc.
        self.repairs = repairs
        self.HOA = HOA #monthly
        self.managementFee = mngFee
        self.water = water
        self.electric = electric
        self.trash = trash
        self.gas = gas
        self.internet = internet
        self.insurance = insurance
        self.interestRate = interestRate
        self.yearsTillPayoff = yearsTillPayoff
        self.chargedRent= chargedRent

        #Calculated Values
        self.totalExpense = 0
        self.baseRent = 0
        self.potentialCashFlow = np.zeros(4, dtype=float)
        self.rentalExpenses = np.zeros(4, dtype=float)
        self.expenses = np.zeros(4, dtype=float)
        self.downPayment = np.zeros(4, dtype=float)
        self.ROI = np.zeros(4, dtype=float)
        pass

    def calcMonthlyExpenses(self,*expenses):
        totalExpenses = 0
        for expense in range(0, len(expenses)):
            totalExpenses += expenses[expense]
        return totalExpenses

    def createHouse(self, lotPervious, lotImpervious, numPeople = 2):
        #Base Prices
        self.downPayment = [(0.05 * self.purchasePrice), (0.10 * self.purchasePrice), (0.15 * self.purchasePrice), (0.2 * self.purchasePrice)]
        purchase = np.full(4, self.purchasePrice, dtype=float)
        loan = purchase - self.downPayment

        if self.chargedRent == 0:
            self.baseRent = self.purchasePrice * 0.011  # calculating avg rent as 1.1% of house price
            self.chargedRent = self.baseRent


        for loanAmt in range(0, len(loan)):
            mortgage = -1 * np.pmt(self.interestRate / 12, self.yearsTillPayoff * 12, loan[loanAmt]) #calcAmoritized(self.purchasePrice, downPayment) #note downPayment is an array

            #Non-dependent expenses
            # Calculate Expenses
            bills = self.calcTotalBills(lotPervious, lotImpervious, numPeople)

            #For rental
            self.rentalExpenses[loanAmt] = self.calcMonthlyExpenses(bills, mortgage, (self.chargedRent * self.managementFee), self.HOA, (self.chargedRent * self.avgVacancy), (self.chargedRent * self.avgCapitalExpenditures),(self.chargedRent * self.repairs), (self.annualTax / 12))
            self.potentialCashFlow[loanAmt] = ((self.chargedRent * 12) - (self.rentalExpenses[loanAmt] * 12))

            #For ownership
            self.expenses[loanAmt] = self.calcMonthlyExpenses(bills, mortgage, self.HOA, (self.chargedRent * self.avgCapitalExpenditures),(self.chargedRent * self.repairs), (self.annualTax / 12)) + self.internet


        self.calcROI()
        print("\n", self.address)
        print("\n Rental Info:")
        print("Total Rental Expenses", self.rentalExpenses)
        print("Potential Cash Flow", self.potentialCashFlow / 12)
        print("Rent", self.chargedRent)
        print("ROI",self.ROI)
        print("\n Generic (nancies:")
        print("Mortgage", mortgage)
        print("Loan Size", loan)
        print("Total Expenses",self.expenses)
        print("\nBills breakdown:")
        print("management fee", (self.managementFee * self.chargedRent))
        print("Water", self.water)
        print("electric", self.electric)
        print("gas", self.gas)
        print("Insurance", self.insurance)

        return 1

    def calcTotalBills(self, lotPervious, lotImpervious, numPeople = 2):
        if self.calcUtilities == True:
            self.water = self.calcWaterBill(lotPervious, lotImpervious, numPeople)
            self.electric = self.calcElectricBill()
            self.gas = self.calcGasBill()
            self.insurance = self.calcInsuranceCost()

        bills = self.water + self.electric + self.trash + self.gas + self.insurance

        return bills

    def calcWaterBill(self, lotPervious, lotImpervious, nPeople):
        #includes water and sewage
        galUsage = [0, 2244, 5236, 7480, 9724, 11968, 14212] #highest average usage for each number of persons
        #Cost per 1000 gallons, note that for each 1000, the price is different (over 14,000 it is constant)
        galCost = [2.84, 2.84, 2.84, 3.26, 3.26, 3.26, 3.60, 3.60, 3.60, 4.50, 4.50, 4.50, 5.07]


        projUse = galUsage[nPeople]
        curGal = 0
        waterBill = 0
        sewageBill = 0
        while projUse > 1000:
            projUse -= 1000
            waterBill += galCost[curGal]
            sewageBill += 2.74
            curGal += 1

        #calculate the remainder
        projUse /= 1000
        waterBill += projUse * galCost[curGal]
        sewageBill += projUse * 2.74

        waterBill = waterBill + 5.70 + 2.03 #add fixed charges
        sewageBill = sewageBill + 14.49 + 0.4
        stormWater = (0.18 * (lotPervious/1000)) + (2.38 * (lotImpervious/1000))

        bill = waterBill + sewageBill + stormWater

        return bill

    def calcElectricBill(self):
        avgUse = 1000 #kWh per month
        gridConn = 31 * 0.62706 #rough estimate per month
        bill = (avgUse * 0.03356) + (avgUse * 0.10807)

        return bill

    def calcGasBill(self):
        avgUse = 60 #therms/month
        bill = (avgUse * 0.1167) + (avgUse * 0.0135) + (avgUse * 0.3779) + (31 * 0.7195)
        return  bill

    def calcInsuranceCost(self):
        bill = (self.purchasePrice / 1000) * 3.50
        return bill / 12

    def calcROI(self):
        ROI = 0
        self.ROI = self.potentialCashFlow / self.downPayment

        return ROI

    def display(self):
        #Once everything is calculated, we need a clever way to display it all
        #We have the rental values, including ROI, and monthly payments calculated
        #Note ROI is a percentage per year

        return 1

def excelReader(filename):
    houseObjects = []
    df1 = pd.read_excel(filename)
    df = df1.where((pd.notnull(df1)), None)

    for index, row in df.iterrows():
        chargedRent = row[5] or 0
        vacancy = row[6] or 0.05
        repairs = row[7] or 0.08
        avgCapX = row[8] or 0.05
        HOA = row[9] or 0
        mngFee = row[10] or 0.01
        water = row[11] or 0
        electric = row[12] or 0
        trash = row[13] or 0
        gas = row[14] or 0
        internet = row[15] or 0
        insurance = row[16] or 0
        calcUtilities = row[17] or 0

        if calcUtilities == -1.0:
            calcUtilities = False
        else:
            calcUtilities = True

        houseObjects.append(housingInvestment(row[0], row[1], row[2], row[3], row[4], chargedRent, vacancy, repairs, avgCapX, HOA, mngFee, water, electric, trash, gas, internet, insurance, calcUtilities))

    for x in range(0, len(houseObjects)):
        houseObjects[x].createHouse(1000, 1000, 2)
    return 1

if __name__ == "__main__":
    excelReader('Houses.xls')
    #house = housingInvestment(115000, 1767.16, 0.03, 15, mngFee=0.06, chargedRent = 1275, HOA=58.435, avgCapX=0, vacancy=0, repairs=0, water=0, internet=0, electric=0, gas=0, trash=0, insurance=86.83, calcUtilities = False)
    #house.createHouse(1000, 1000, 2)

