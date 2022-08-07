# importing main libraries/modules
import os
import pandas as pd
import numpy as np

# importing data visualization libraries
import matplotlib.pyplot as plt
import seaborn as sns 
sns.set()

# sklearn library for data science
from sklearn.model_selection import train_test_split
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.metrics import mean_squared_error

# import datetime module
import datetime

# importing mysql
import env
from env import user, password, host, get_connection

from math import sqrt


'''function that will either 
1. import the zillow dataset from MySQL or 
2. import from cached .csv file'''
def get_zillow_dataset():
    # importing "cached" dataset
    filename = "zillow.csv"
    if os.path.isfile(filename):
        return pd.read_csv(filename, index_col=[0])

    # if not in local folder, let's import from MySQL and create a .csv file
    else:
        # query used to pull the 2017 properties table from MySQL
        query = ''' 
        SELECT prop.*,
        predictions_2017.logerror,
        predictions_2017.transactiondate,
        air.airconditioningdesc,
        arch.architecturalstyledesc,
        build.buildingclassdesc,
        heat.heatingorsystemdesc,
        land.propertylandusedesc,
        story.storydesc,
        type.typeconstructiondesc
        FROM properties_2017 prop
        JOIN (
            SELECT parcelid, MAX(transactiondate) AS max_transactiondate
            FROM predictions_2017
            GROUP BY parcelid
            ) pred USING(parcelid)
        JOIN predictions_2017 ON pred.parcelid = predictions_2017.parcelid
                          AND pred.max_transactiondate = predictions_2017.transactiondate
        LEFT JOIN airconditioningtype air USING(airconditioningtypeid)
        LEFT JOIN architecturalstyletype arch USING(architecturalstyletypeid)
        LEFT JOIN buildingclasstype build USING(buildingclasstypeid)
        LEFT JOIN heatingorsystemtype heat USING(heatingorsystemtypeid)
        LEFT JOIN propertylandusetype land USING(propertylandusetypeid)
        LEFT JOIN storytype story USING(storytypeid)
        LEFT JOIN typeconstructiontype type USING(typeconstructiontypeid)
        WHERE propertylandusedesc = "Single Family Residential"
            AND transactiondate <= '2017-12-31'
            AND prop.longitude IS NOT NULL
            AND prop.latitude IS NOT NULL
        '''
        
        db_url = f'mysql+pymysql://{user}:{password}@{host}/zillow'

        # creating the zillow dataframe using Pandas' read_sql() function
        df = pd.read_sql(query, db_url)
        df.to_csv(filename)

        return df


'''Preparing/cleaning zillow dataset
focus is dropping Null values and changing column types'''
def clean_zillow_dataset(df):

    # handling initial feature nulls
    max_null_percentage = 0.20
    min_record_percentage = 0.8

    for col in list(df.columns):
    
        null_sum = df[col].isna().sum()
        null_pct = null_sum / df.shape[0]
        
        if null_pct > max_null_percentage:
            df.drop(columns=col, inplace=True)
    
    feature_threshold = int(min_record_percentage * df.shape[1])
    
    df = df.dropna(axis = 0, thresh = feature_threshold)

    # cleaning df for records with < 50ft. of living space 
    df = df[df["calculatedfinishedsquarefeet"] >= 50]

    # cols needed for initial exploration & hypothesis testing
    df = df[[
    'parcelid',
    'taxvaluedollarcnt',
    'logerror',
    'bathroomcnt',
    'bedroomcnt',
    'calculatedfinishedsquarefeet',
    'fips',
    'latitude',
    'longitude',
    'lotsizesquarefeet',
    'propertycountylandusecode',
    'rawcensustractandblock',
    'transactiondate',
    'yearbuilt'
    # 'landtaxvaluedollarcnt',
    # 'structuretaxvaluedollarcnt',
    # 'taxamount'
    ]]

    # renaming cols
    df = df.rename(columns = {
    'parcelid': "parcel_id",
    'taxvaluedollarcnt': "home_value",
    'bathroomcnt': "bathroom_count",
    'bedroomcnt': "bedroom_count",
    'calculatedfinishedsquarefeet': "living_sq_feet",
    'fips': "county_by_fips",
    'lotsizesquarefeet': "property_sq_feet",
    'propertycountylandusecode': "county_zoning_code",
    'rawcensustractandblock': "blockgroup_assignment",
    'transactiondate': "transaction_date",
    'yearbuilt': "year_built"
    # 'landtaxvaluedollarcnt': "land_assessed_value",
    # 'structuretaxvaluedollarcnt': "home_assessed_value"
})

    # editing block id
    df["blockgroup_assignment"] = df["blockgroup_assignment"].astype(str)

    # editing parcel id
    df["parcel_id"] = df["parcel_id"].astype(str)

    # converting fips_code to county
    df["county_by_fips"] = df["county_by_fips"].replace(
        [6037.0, 6059.0, 6111.0], \
        ["LA County", "Orange County", "Ventura County"])

    # converting the following cols to proper int type
    # df["year_built"] = df["year_built"].astype(int)

    # converting purchase date to datetime type
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format = '%Y/%m/%d')

    # returning the cleaned dataset
    print(f'dataframe shape: {df.shape}')

    return df


'''Function takes in the original zillow dataset and returns a new column/feature
called "transaction_month" which is the month when the home was sold/purchased'''
def clean_months(df):
    # mapping existing date to just year and month of transaction
    df['transaction_month'] = pd.to_datetime(df.transaction_date).dt.strftime('%m/%Y')

    # renaming month-year column to months only
    year_and_month = df["transaction_month"].sort_values().unique().tolist()
    month_lst = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']

    df["transaction_month"] = df["transaction_month"].replace(
        year_and_month,
        month_lst)

    # dropping transaction date column/feature and keeping solely purchase month information
    df.drop(columns = "transaction_date", inplace = True)

    return df 


'''Function to calculate total age of the home through present year 
based on the year it was built'''
def age_of_homes(df):
    # creating a column for age of the home
    year_built = df["year_built"]
    # curr_year = datetime.datetime.now().year

    # placing column/series back into main df
    df["home_age"] = 2017 - year_built

    return df



'''Function takes in a dataframe and returns a feature/column total null count and percentage df'''
def null_df(df):
    # creating a container to hold all features and needed null data
    container = []

    for col in list(df.columns):
        feature_info = {
            "Name": col, \
            "Total Null": df[col].isnull().sum(), \
            "Feature Null %": df[col].isnull().sum() / df.shape[0]
        }
        # appending feature and data to container list
        container.append(feature_info)
        
    # creating the new dataframe
    new_df = pd.DataFrame(container)

    # setting the df index to "name"
    new_df = new_df.set_index("Name")

    # setting index name to None
    new_df = new_df.rename_axis(None, axis = 0)

    # sorting df by percentage of null descending
    new_df = new_df.sort_values("Total Null", ascending = False)

    # returning the new null dataframe
    return new_df


'''function to drop columns/rows based on proportion of nulls across record and feature'''
def drop_nulls(df, required_column_percentage, required_record_percentage):
    
    feature_null_percentage = 1 - required_column_percentage
    
    for col in list(df.columns):
        
        null_sum = df[col].isna().sum()
        null_pct = null_sum / df.shape[0]
        
        if null_pct > feature_null_percentage:
            df.drop(columns=col, inplace=True)
            
    feature_threshold = int(required_record_percentage * df.shape[1])
    
    df = df.dropna(axis = 0, thresh = feature_threshold)
    
    return df


'''Function created to split the initial dataset into train, validate, and test datsets'''
def train_validate_test_split(df):
    train_and_validate, test = train_test_split(
    df, test_size = 0.2, random_state = 123)
    
    train, validate = train_test_split(
        train_and_validate,
        test_size = 0.3,
        random_state = 123)

    print(f'train shape: {train.shape}')
    print(f'validate shape: {validate.shape}')
    print(f'test shape: {test.shape}')

    return train, validate, test



'''Functions determines outliers based on iqr upper-bound, and returns a dataframe with
feature name, upper-bound, and total number of outliers above upper-bound'''
def sum_outliers(df, k = 1.5):
    
    # placeholder for df values
    uppercap_df = []

    for col in df.select_dtypes("number"):
        # removing the target variable
        if col != "logerror":
            # determing 1st and 3rd quartile
            q1, q3 = df[col].quantile([.25, 0.75])

            # calculate interquartile range
            iqr = q3 - q1

            # set feature/data upperbound limit
            upper_bound = q3 + k * iqr

            # boolean mask to determine total number of outliers
            mask = df[df[col] > upper_bound]

            if mask.shape[0] > 0:

                output = {
                    "Feature": col, \
                    "Upper_Bound": upper_bound, \
                    "Total Outliers": mask.shape[0]
                    }

                uppercap_df.append(output)
    
    new_df = pd.DataFrame(uppercap_df).sort_values(by = "Total Outliers", ascending = False, ).reset_index(drop = True)
    
    return new_df


'''Function determines outliers based on "iqr" and then capps outliers at upper-bound'''
def capp_outliers(df, k = 1.5):
    
    num_lst = df.select_dtypes("number").columns.tolist()
    num_lst = [ele for ele in num_lst if ele not in ("parcel_id", 'longitude', 'latitude', 'blockgroup_assignment')]

    # determining continuous features/columns
    for col in df[num_lst]:
        
        # determing 1st and 3rd quartile
        q1, q3 = df[col].quantile([.25, 0.75])
        
        # calculate interquartile range
        iqr = q3 - q1
        
        # set feature/data lower bound limit
        lower_bound = q1 - k * iqr

        # set feature/data upperbound limit
        upper_bound = q3 + k * iqr
        
        # lower cap/convert outliers to lower bound
        df[col] = df[col].apply(lambda x: lower_bound if x < lower_bound else x)

        # upper cap/convert outliers to upper bound
        df[col] = df[col].apply(lambda x: upper_bound if x > upper_bound else x)
    
        # renaming the column to reflect capping
        df.rename(columns = {col: col + "_capped"}, inplace = True)

    # returning the updated dataframe
    return df



# using sklearn's iterative imputer to fill-in remaining nulls
def train_iterative_imputer(train_df):

        # placeholder for continuous features
        num_lst = [
        'home_value_capped',
        'bathroom_count_capped',
        'bedroom_count_capped',
        'living_sq_feet_capped',
        'latitude',
        'longitude',
        'property_sq_feet_capped',
        'blockgroup_assignment_capped',
        'year_built',
        'home_age_capped']

        # creating the "thing"
        imputer = IterativeImputer(
                missing_values = np.nan, \
                skip_complete = True, \
                random_state = 123)
        
        # fitting the "thing" and transforming it
        imputed = imputer.fit_transform(train_df[num_lst])

           # create a new dataframe with learned imputed data
        train_df_imputed = pd.DataFrame(imputed, index = train_df.index)

        # filling in missing values from learned imputer
        train_df[num_lst] = train_df_imputed

        # return the new imputed df
        return train_df


# function establishes a baseline for train and validate - will be used for model comparison:
def establish_baseline(train, validate):

    baseline = round(train["logerror_capped"].mean(), 2)

    train['baseline'] = baseline
    validate['baseline'] = baseline

    train_rmse = sqrt(mean_squared_error(train.logerror_capped, train.baseline))
    validate_rmse = sqrt(mean_squared_error(validate.logerror_capped, validate.baseline))

    print('Train baseline RMSE: {:.2f}'.format(train_rmse))
    print('Validate baseline RMSE: {:.2f}'.format(validate_rmse))

    train = train.drop(columns = "baseline")
    validate = validate.drop(columns = "baseline")
    print()
    print(f'train shape: {train.shape}')
    print(f'validate shape: {validate.shape}')

    return train, validate

'''-----------------------------------'''
# borrowed/previous lesson functions

def remove_columns(df, cols_to_remove):
    df = df.drop(columns=cols_to_remove)
    return df

def handle_missing_values(df, prop_required_columns=0.5, prop_required_row=0.75):
    threshold = int(round(prop_required_columns * len(df.index), 0))
    df = df.dropna(axis=1, thresh=threshold) #1, or ‘columns’ : Drop columns which contain missing value
    threshold = int(round(prop_required_row * len(df.columns), 0))
    df = df.dropna(axis=0, thresh=threshold) #0, or ‘index’ : Drop rows which contain missing values.
    return df


# combining both functions above in a cleaning function:
def data_prep(df, cols_to_remove=[], prop_required_column=0.5, prop_required_row=0.75):
    df = remove_columns(df, cols_to_remove)
    df = handle_missing_values(df, prop_required_column, prop_required_row)
    return df

'''
Given a series and a cutoff value, k, returns the upper outliers for the
series.

The values returned will be either 0 (if the point is not an outlier), or a
number that indicates how far away from the upper bound the observation is.
'''
def get_upper_outliers(s, k=1.5):

    q1, q3 = s.quantile([.25, 0.75])

    # generating interquantile range
    iqr = q3 - q1

    # creating the feature upperbound
    upper_bound = q3 + (k * iqr)

    # creating a dataframe of feature upperbound
    df = pd.DataFrame(s.apply(lambda x: max([x - upper_bound, 0])))
    
    return df

'''Add a column with the suffix _outliers for all the numeric columns
in the given dataframe'''
def add_upper_outlier_columns(df, k=1.5):
    
    # iterate through all dataframe columns and check for numerical type columns
    for col in df.select_dtypes('number'):
        df[col + '_outliers_upper'] = get_upper_outliers(df[col], k)
    
    df = df.reset_index(drop = True)

    return df