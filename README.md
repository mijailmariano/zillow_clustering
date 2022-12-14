## Machine Learning: Unsupervised Clustering

### Zillow Real Estate Dataset
----

##### Created by: Mijail Q. Mariano
##### github.com/mijailmariano

<br>

### **<u>Project Description & Goals:</u>**

This analysis is a continuation of my ``Zillow Regression Analysis`` that may be found here: **<a href="https://github.com/mijailmariano/zillow_regression" target="_blank">Zillow Regression Analysis </a>**

The intent of this project is to leverage unsupervised machine learning clustering techniques to help reframe how we think about real-estate information, and make improvements to accurately assess and predict a home's value.

In this analysis I use Zillow's "Zestimate"/prediction home value error as measured by the **logarithmic error** in the dataset as the predicted target variable and quality measure of the clusters I create to better explain the home value story.  

``logerror = log(Predicted: Zestimate) − log(Actual: Home Transaction Price)``

----
<u>**``In Brief:``**</u>

1. I first acquired and cleaned a Zillow 2017 real-estate dataset
2. I used an “Inter-Quartile Range” (IQR) method to determine outliers in the dataset and filtered out homes over the 1.2 million dollar valuation, as this proved to be well over the median single-family household range for the state of California.*
3. I identified and treated missing values using a K-nearest neighbor imputer method
4. I created and tested statistical hypotheses to explore the market trends that I was curious about
5. To uniquely segment the real-estate data I bin and group dataset features to create classification clusters and used these clusters in unsupervised machine learning models
6. I create three (3) distinctly grouped feature clusters

**"Monthly Clusters"**

    A home's total property square feet and the calendar month that a home's transaction is recorded.

**"Era Clusters"**

    A home's total living square feet and the period or era in which the home was built.

**"Home Size Clusters"**

    A home's total age in years through 2017 and the size range of a home as measured in living square feet.

7. I use SKLearn's RFE in conjuction with linear & non-linear regression models to test the quality of the clusters in predicting logerror.

**Linear Models**

    - Linear Regression
    - Tweedie Regressor
    - Lasso Lars 


**Non-linear Models**

    - Polynomial w/Degree 2
    - Principal Component Analysis (PCA)

8. I deployed the clusters I created with both linear and non-linear statistical models to predict logarithmic error
9. Finally, I evaluated the performance of my models and generated recommendations for follow-on analysis and implementation of my findings 



<br></br>

*I believe that homes over the 1.2mil USD evaluation would warrant another distinct analysis & modeling processing.* * 

----
#### **<u>Exploration Questions & Hypotheses:</u>**

**1. Is there a difference in logerror across transaction month?**

Given the many economic factors that may influence the housing market, I belive that this could also lead to challenges in accurate and timely home evaluations - thus leading to over, or under estimating a home's true value.

**Months in Analysis**

    January
    February
    March
    April
    May
    June
    July
    August
    September


**2. Is there a difference in logerror across home sizes?**

Social and cultural changes such as the age/period of first-time families, interests in more sustainable and smaller eco-friendly lifestyles can all play a role in determining the size value of a home. I believe factors such as these can undoubtedbly make predicting the precise true value of a home more difficult.

**Bins by Home Size**

    360 - 1241 sq. ft (smallest)
    1241 - 1566 sq. ft
    1566 - 2037 sq. ft
    2037 - 3855 sq. ft (largest)


**3. Is there a difference in logerror across home building eras?**

As time passes so do the architectural design methods and the kinds of homes that are built. For example, colonial style homes may be reminiscent of a 17th-18th century time period. 

A mid-century modern design home - may provide a feeling of both nostalgia and future creativity. In either case, I believe that as time passes so do the building styles of home and ultimately which home styles are more prevailing in current times. Unfortunately, similar to home styles - these preference trends are just as difficult to predict but could be valuable to understand. 


**Bins of Home Building Eras**

    1977 - 2015: New Century
    1960 - 1976: Late 20th Century
    1950 - 1959: Mid 20th Century
    1907 - 1949: Early 20th Century

----

### <u>**Statistically Significant Model Features**</u>

</br>

| Ranking       | Feature       | Characteristic       |
| ----          | ----          | ----                 |
| 1     | size_clusters_1       | 1241-1566 sq. ft     |
| 2     | era_clusters_3        | Early 20th Century   |
| 3     | era_clusters_2        | Mid 20th Century     |
| 4     | era_clusters_0        | New Century          |
| 5     | month_clusters_4      | May                  |
| 6     | month_clusters_0      | June                 |
| 7     | size_clusters_0       | 360-1241 sq. ft      |
| 8     |month_clusters_6       | January              |
| 9     | size_clusters_2       | 1566-2037 sq. ft     |
| 10    | month_clusters_8      | April                |
| 11    | month_clusters_1      | August               |
| 12    | month_clusters_3      | July                 |
| 13    | month_clusters_2      | March                |
| 14    | month_clusters_7      | September            |
| 15    | size_clusters_3       | 2037-3855 sq. ft     |



<br>

| RFE non-selected      | Characteristic            |
| ----                  | ----                      |
| era_clusters_1        | Late 20th Century         |
| month_clusters_5      | February                  |

----

### **<u>Model Results</u>**

* Training R-squared w/Linear Regression: 0.0103
* Training R-squared w/Lasso Lars: 0.0
* Training R-squared w/Tweedie Regressor: 0.0031

<br>

|Model|Train RMSE|Validate RMSE|
|----|----|----|
|pca|0.05|0.05|
|polynomial deg. 2|0.05|0.05|
|linear regression|0.05|0.05|
|lasso lars|0.05|0.05|
|tweedie regressor|0.05|0.05|
|baseline mean|0.05|0.05|

<br>


----

<u>**``Polynomial Regression Performance Through Test Dataset``**</u>

|Polynomial Deg. 2 Model Performance|RMSE|Relative % Difference|
|----|----|----|
|Baseline|0.05|0.0|
|Train|0.05|0.0|
|Validate|0.05|0.0|
|Test (final)|0.05|0.0|


----

### **``Recommendations:``**


Conducting a “build home-style” analysis to record the differences across era architectural styles and test whether or not the unique architectural design styles of a home can directly impact its predicted home value. 

I would incentivize and elicit through surveys what unique design features home sellers or potential buyers have included in their homes and/or look for in a new home. This can also help us to understand homes’ unique internal design components that have been introduced over the years and test whether or not this helps to tell the home value story.



----

### **Looking Ahead (next steps):**

* Acquire full year Zillow dataset for analysis
* Attempt to view and segment the transaction periods in other meaningful ways (i.e., weekly, bi-monthly, quarters, bi-yearly snapshots)
* Convert longitude and latitude to proper plotting coordinates and measure their relationship to logerror/home value to include other geographical features (i.e., zip code, blockgroup assignment code, county zoning code)

----
### **<u>Repository Roadmap:</u>**

Below is a file breakdown on how to best navigate this GitHub repository and the subsequent analysis. All code, data synthesis, and models can be found here for future reproduction or improvements:

1. **final_report.ipynb**

   Data Science pipeline overview document. Project artifact of the hypothesis tests conducted, regression techniques used for machine learning models, key analysis takeaways, and recommendations.

2. **data_exploration.ipynb**

   Jupyter Notebook used as the data science pipeline file which walks-through the process for creating the necessary data acquisition and cleaning functions.

3. **acquire.py** 
  
   Python module file that imports the neccessary Zillow real-estate dataset and subsequent feature for modeling phase in the analysis. If just using or running the final_report.ipynb file, then this corresponding acquire.py file should suffice and the prepare.py file will not be needed.
   
   **Note:** you must first import the initial Zillow dataset from MySQL. When passed in the "acquire.get_zillow_dataset()" function, the data is then stored locally as a .csv file - then referenced as a pd.Dataframe thereafter. 

4. **prepare.py**

     Python module file with created functions needed to clean, and manipulate the Zillow dataset used in this analysis.

<br>

----

## <center> **Data Dictionary** </center>

home_age:
- total age of the home in years

latitude:
- relative north/south location of the home

living_sq_feet:
-  calculated total finished living area of the home 

fips_code_6037:
- federal info. processing standard code (Los Angeles, California)

fips_code_6059:
- federal info. processing standard code (Orange, California)

fips_code_6111:
- federal info. processing standard code (Ventura, California)

Transaction_month_April:
- home transaction/purchased in the month of April

Transaction_month_August:
- home transaction/purchased in the month of August

Transaction_month_January:
- home transaction/purchased in the month of January

Transaction_month_July:
- home transaction/purchased in the month of July

Transaction_month_March:
- home transaction/purchased in the month of March

Transaction_month_May:
- home transaction/purchased in the month of May

Transaction_month_September:
- home transaction/purchased in the month of September

