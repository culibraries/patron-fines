import sys
import pandas as pd 
import calendar
from pandas.tseries.offsets import MonthEnd
from dateutil import relativedelta
def parse(series):
    list1=[]
    list2=[]
    list3=[]
    for item in list(series):
        if '$' in item: 
            #print(item)
            try:
                tmp1,tmp2=item.split('$')
                tmp3=""
            except:
                tmp1,tmp2,tmp3=item.split('$')
            list1.append(tmp1)
            list2.append(tmp2)
            list3.append(tmp3)
        else:
            list1.append(item)
            list2.append("")
            list3.append("")
    return list1, list2, list3

def currencyformat(x):
    return int(x/100)

def labels(row):
    if row['TYPE'] == 'OVERDUE':
        row['Amount3'] =row['Amount']
        row['AmtTotal']= row['Amount']
        row['Amount']='0'
        row['Amount2']='0'
        if int(row['Amount3']) >0:
            row['LblAmt'] = 'NA'
            row['LblAmt2'] ='NA'
            row['LblAmt3'] ='Fine'
    elif row['TYPE'] =='MANUAL':
        if int(row['AmtTotal']) > 0:
            row['LblAmt'] = 'NA'
            row['LblAmt2'] ='NA'
            row['LblAmt3'] ='Fine'
    elif row['TYPE'] =='OVERDUEX':
        if int(row['Amount']) < 0 and int(row['Amount2']) < 0 and int(row['Amount3'])>= 0:
            row['LblAmt'] = 'Rep Credit'
            row['LblAmt2'] ='Rep Proc Fee Credit'
            row['LblAmt3'] ='Fine'
        if int(row['Amount']) < 0 and int(row['Amount2']) == 0 and int(row['Amount3'])== 0:
            row['LblAmt'] = 'Rep Credit'
            row['LblAmt2'] ='NA'
            row['LblAmt3'] ='NA'
        if int(row['Amount']) < 0 and int(row['Amount2']) == 0 and int(row['Amount3']) > 0:
            row['LblAmt'] = 'Rep Book Credit'
            row['LblAmt2'] ='NA'
            row['LblAmt3'] ='BRS'
    elif row['TYPE'] =='REPLACEMENT' or row['TYPE'] =='LOST':
        if int(row['Amount']) < 0 and int(row['Amount2']) == 0 and int(row['Amount3']) == 0:
            row['LblAmt'] = 'Rep Book Credit'
            row['LblAmt2'] ='NA'
            row['LblAmt3'] ='NA'
        if int(row['Amount']) < 0 and int(row['Amount2']) < 0 and int(row['Amount3']) > 0:
            row['LblAmt'] = 'Rep Credit'
            row['LblAmt2'] ='Rep Proc Fee Credit'
            row['LblAmt3'] ='Fine'
        if int(row['Amount']) > 0 and int(row['Amount2']) == 0 and int(row['Amount3']) > 0:
            row['LblAmt'] = 'Rep Charge'
            row['LblAmt2'] ='NA'
            row['LblAmt3'] ='Bill Fee'
        if int(row['Amount']) > 0 and int(row['Amount2']) > 0 and int(row['Amount3']) == 0:
            row['LblAmt'] = 'Rep Charge'
            row['LblAmt2'] ='Rep Proc Fee'
            row['LblAmt3'] ='NA'
        if int(row['Amount']) > 0 and int(row['Amount2']) > 0 and int(row['Amount3']) > 0:
            row['LblAmt'] = 'Rep Charge'
            row['LblAmt2'] ='Rep Proc Fee'
            row['LblAmt3'] ='Bill Fee'
        if int(row['Amount']) < 0 and int(row['Amount2']) < 0 and int(row['Amount3']) == 0:
            row['LblAmt'] = 'Rep Credit'
            row['LblAmt2'] ='Rep Proc Fee Credit'
            row['LblAmt3'] ='NA'
    return row

def last_business_day_in_month(year: int, month: int) -> int:
    return max(calendar.monthcalendar(year, month)[-1:][0][:5])

def transform(filename):
    #LineNum
    df=pd.read_csv(filename,sep='|',engine='python' )
    header = list(df.columns)
    transc_date=pd.to_datetime(header[-1],format='%y%m%d',errors='ignore').date()
    df=pd.read_csv(filename,sep='|',skiprows=1,header=None,engine='python' )
    linenum= [transc_date.strftime('1%m%d%y') + ('0000' + str(i))[-4:] for i in range(1,(len(df)+1))]
    df.insert(0, 'LineNum', linenum)
    #InvoiceNo
    df=df.rename(columns={0: "InvoiceNo"})
    #InvDate
    df[1] = pd.to_datetime(df[1].astype(str), format='%y%m%d')
    df[1] = df[1].apply(lambda x: x.strftime('%m/%d/%Y'))
    #Column rename
    df=df.rename(columns={1: "InvDate",2:"Location",3:"PatronNo",4:"ID"})
    #Names split
    name1,name2,junk=parse(df[5])
    df[5]=name1
    df=df.rename(columns={5: "Name"})
    df.insert(7, 'Name2', name2)
    #Address split
    addr1,addr2,country=parse(df[6])
    df[6]=addr1
    df=df.rename(columns={6: "Address1"})
    df.insert(9, 'Address2', addr2)
    df.insert(10, 'Country', country)
    df=df.rename(columns={7:"P1",8:"P2",9:"P3",10:"pType",11:"ItemBarcode",12:"ItemTitle",13:"CallNo",14:"TYPE",15:"Amount",16:"Amount2",17:"Amount3"})
    # Truncate Title 255 char
    df['ItemTitle']=df['ItemTitle'].str.slice(0,254)
    #Amounts
    df['Amount']=df['Amount'].apply(currencyformat)
    df['Amount2']=df['Amount2'].apply(currencyformat)
    df['Amount3']=df['Amount3'].apply(currencyformat)
    df['AmtTotal'] = df["Amount"] + df["Amount2"] + df["Amount3"]
    # Dates
    df['RprtDate']=transc_date.strftime('%m/%d/%Y')	
    df['CutOffDate']=transc_date.replace(day = last_business_day_in_month(transc_date.year, transc_date.month)).strftime('%m/%d/%Y')	
    next_month=(transc_date + relativedelta.relativedelta(months=1)).month
    next_year=(transc_date + relativedelta.relativedelta(months=1)).year
    df['DueDateInv']=transc_date.replace(month= next_month , year=next_year, day = last_business_day_in_month(next_year, next_month)).strftime('%m/%d/%Y')
    # Add Additional columns
    df['CheckNo']=""
    df['DatePaid']=""
    df['AmtPaid']=""
    df['WhoEntered']=""
    df['DateToCashiers']=""
    df['AcctStatus']=""
    df['DateNoticeSent']=""
    df['DateToCollection']=""
    df['PaidOKToMove']=""
    df['Notes']=""
    df['LblAmt']=""
    df['LblAmt2']=""
    df['LblAmt3']=""
    df['AmtTotal1']="AmtTotal1"
    # Apply Labels
    df=df.apply(labels,axis=1)
    return df

# if __name__ == "__main__":
#     result=[]
#     inputs=sys.argv[1].split(',')
#     for item in inputs:
#         result.append(transform(item))
#     df=pd.concat(result,ignore_index=True)
#     df.to_csv(sys.argv[2],sep='|',index=False)
    