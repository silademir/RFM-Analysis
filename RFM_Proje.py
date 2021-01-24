############################################
# PROJE: RFM ile Müşteri Segmentasyonu
############################################


# Değişkenler
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara.
# Eğer bu kod C ile başlıyorsa işlemin iptal edildiğini ifade eder.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_columns", None)

data = pd.read_excel("datasets/online_retail_II.xlsx",
                   sheet_name="Year 2010-2011")
df = data.copy()
df.head()
df.isnull().values.any()
df.info()

# Null Values

null_values = pd.DataFrame(df.isnull().sum(), columns=["values"])
sns.barplot(null_values["values"], null_values.index)
plt.show()

df.dropna(inplace=True)

# Eşsiz Ürün Sayısı
df["Description"].nunique()

# Hangi üründen kacar tane var?
df["Description"].value_counts()

# En cok siparis edilen ürün
df.groupby("Description").agg({"Quantity": "sum"}).sort_values(by="Quantity",
                                                                ascending=False)
# Toplam kac fatura kesilmis?
df["Invoice"].nunique()

# Fatura basına ortalama kac para kazanılmıstır?
# İlk önce iadeleri cıkartmalıyız

df = df[~df["Invoice"].str.contains("C", na=False)]
df["Total Price"] = df["Price"] * df["Quantity"]
df.head()

# En pahalı ürünler hangisi?
df.sort_values(by="Price",
                ascending=False)

# Hangi ülkeden kac siparis geldi?
df["Country"].value_counts()

# Hangi ülke ne kadar kazandırdı?
df.groupby("Country").agg({"Total Price": "sum"}).sort_values("Total Price",
                                                               ascending=False).head()

###############################################################
# Calculating RFM Metrics
###############################################################

# Recency, Frequency, Monetary

# Recency (yenilik): Müşterinin son satın almasından bugüne kadar geçen süre
# Diğer bir ifadesiyle “Müşterinin son temasından bugüne kadar geçen süre” dir.

# Bugünün tarihi - Son satın alma

df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda x: (today_date - x.max()).days,
                                      'Invoice': lambda x: len(x),
                                      'Total Price': lambda x: x.sum()})

rfm.columns = ["Recency", "Frequency", "Monetary"]
rfm = rfm[(rfm["Monetary"] > 0) & (rfm["Frequency"] > 0)]

###############################################################
# Calculating RFM Scores
###############################################################

# Recency
rfm["RecencyScore"] = pd.cut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])

rfm["FrequencyScore"] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4, 5])

rfm["MonetaryScore"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) +
                    rfm['FrequencyScore'].astype(str) +
                    rfm['MonetaryScore'].astype(str))

# RFM isimlendirmesi
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}

rfm

rfm["Segment"] = rfm['RecencyScore'].astype(str) + rfm['FrequencyScore'].astype(str)
rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)

rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean", "count"])

#                        Recency         Frequency           Monetary
#                           mean count        mean count         mean count
# Segment
# About_to_Sleep       187.984314   255   13.513725   255   512.034549   255
# At_Risk              295.625000   128   51.929688   128   677.392812   128
# Cant_Loose           302.454545    11  167.545455    11  2316.299091    11
# Champions             23.112188  1444  211.786011  1444  4559.269688  1444
# Hibernating          294.595483   487   13.020534   487   550.141273   487
# Loyal_Customers      129.406926   231  111.926407   231  1703.911519   231
# Need_Attention       184.355556    90   40.588889    90   690.270778    90
# New_Customers         37.175074   337    7.985163   337   931.011306   337
# Potential_Loyalists   51.778055  1203   33.651704  1203   816.162696  1203
# Promising            108.190789   152    7.539474   152   433.189671   152

rfm[rfm["Segment"] == "Loyal_Customers"].head()
rfm[rfm["Segment"] == "Loyal_Customers"].index

new_df = pd.DataFrame()
new_df["Loyal_Customers"] = rfm[rfm["Segment"] == "Loyal_Customers"].index
new_df.to_excel("Loyal_Customers.xlsx")

# Cant_Loose
# Champions
# Loyal Customers