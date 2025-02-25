import pandas as pd
import streamlit as st


def fetch_time_features(df, datetime_col):
    df[datetime_col] = pd.to_datetime(df[datetime_col], errors='coerce')
    df['year'] = df[datetime_col].dt.year
    df['month'] = df[datetime_col].dt.month
    return df

def load_datasets(file_names):
    datasets = {}
    for file_name in file_names:
        dataset_name = file_name.split('.')[0]
        datasets[dataset_name] = pd.read_csv(file_name)
    return datasets

def preprocess_and_insight(datasets):
    orders_df = datasets['olist_orders_dataset']
    orders_df = fetch_time_features(orders_df, 'order_purchase_timestamp')
    datasets['olist_orders_dataset'] = orders_df
    return datasets

def multiselect(title, options_list):
    selected = st.sidebar.multiselect(title, options_list)
    select_all = st.sidebar.checkbox("Select all", value=True, key=title)
    if select_all:
        return options_list
    return selected

import pandas as pd

def fetch_time_features(df, datetime_col):
    df[datetime_col] = pd.to_datetime(df[datetime_col], errors='coerce')
    df['year'] = df[datetime_col].dt.year
    df['month'] = df[datetime_col].dt.month
    return df

def load_datasets(file_names):
    datasets = {}
    for file_name in file_names:
        dataset_name = file_name.split('.')[0]  # Use the file name without extension as the key
        datasets[dataset_name] = pd.read_csv(file_name)
    return datasets

def preprocess_and_insight(datasets):
    # Preprocessing on orders dataset
    orders_df = datasets['olist_orders_dataset']
    orders_df = fetch_time_features(orders_df, 'order_purchase_timestamp')
    
    # Preprocessing on payments dataset
    payments_df = datasets['olist_order_payments_dataset']
    payments_df = payments_df.groupby('order_id', as_index=False).agg({'payment_value': 'sum'})
    
    # Merge datasets for better insights
    datasets['olist_orders_dataset'] = pd.merge(orders_df, payments_df, on='order_id', how='left')
    
    # Ensure all necessary datasets have been cleaned and processed
    for key, df in datasets.items():
        datasets[key] = df.dropna(how='all')  # Drop rows with all values missing
    
    return datasets


def merge_order_items_sellers(order_items_df, sellers_df):
    """
    Merges the 'olist_order_items_dataset' and 'olist_sellers_dataset' on 'seller_id'.
    """
    # Ensure both dataframes have the necessary 'seller_id' column
    if 'seller_id' in order_items_df.columns and 'seller_id' in sellers_df.columns:
        # Merge on 'seller_id'
        merged_df = pd.merge(order_items_df, sellers_df, on='seller_id', how='inner')
        return merged_df
    else:
        raise KeyError("One of the datasets is missing the 'seller_id' column.")


def merge_orders_payments(orders_df, payments_df):
        """
        Merges the 'olist_orders_dataset' and 'olist_order_payments_dataset' on 'order_id'.
        """
        # Ensure both dataframes have the necessary 'order_id' column
        if 'order_id' in orders_df.columns and 'order_id' in payments_df.columns:
            # Merge on 'order_id'
            merged_df = pd.merge(orders_df, payments_df, on='order_id', how='inner')
            return merged_df
        else:
            raise KeyError("One of the datasets is missing the 'order_id' column.")


def load_geolocation_data():
    df = pd.read_csv('olist_geolocation_dataset.csv')
    df['geolocation_lng'] = pd.to_numeric(df['geolocation_lng'], errors='coerce')
    df['geolocation_lat'] = pd.to_numeric(df['geolocation_lat'], errors='coerce')
    return df



@st.cache_data
def load_data():
    """Loads and merges geolocation and seller datasets."""
    geolocation_df = pd.read_csv('olist_geolocation_dataset.csv')
    sellers_df = pd.read_csv('olist_sellers_dataset.csv')
    merged_df = pd.merge(
        sellers_df, 
        geolocation_df, 
        left_on='seller_zip_code_prefix', 
        right_on='geolocation_zip_code_prefix',
        how='left'
    )
    # Drop rows with missing latitude/longitude
    merged_df = merged_df.dropna(subset=['geolocation_lat', 'geolocation_lng'])
    return merged_df

@st.cache_data
def filter_data(merged_df, state_filter, city_filter):
    """Filters the dataset based on selected states and cities."""
    return merged_df[(merged_df['seller_state'].isin(state_filter)) & 
                     (merged_df['seller_city'].isin(city_filter))]

@st.cache_data
def get_map_data(filtered_df):
    """Prepares the map data (latitude and longitude only) for visualization."""
    return filtered_df[['geolocation_lat', 'geolocation_lng']].rename(columns={
        'geolocation_lat': 'latitude', 
        'geolocation_lng': 'longitude'
    })

import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    """Load and merge geolocation and seller datasets."""
    # Load the datasets
    geolocation_df = pd.read_csv('olist_geolocation_dataset.csv')
    sellers_df = pd.read_csv('olist_sellers_dataset.csv')
    
    # Merge datasets on zip code prefix
    merged_df = pd.merge(
        sellers_df, 
        geolocation_df, 
        left_on='seller_zip_code_prefix', 
        right_on='geolocation_zip_code_prefix',
        how='left'
    )
    
    # Drop rows with missing latitude/longitude
    merged_df = merged_df.dropna(subset=['geolocation_lat', 'geolocation_lng'])
    
    return merged_df

@st.cache_data
def filter_data(merged_df, state_filter, city_filter):
    """Filter the dataset based on selected states and cities."""
    filtered_df = merged_df[
        (merged_df['seller_state'].isin(state_filter)) &
        (merged_df['seller_city'].isin(city_filter))
    ]
    return filtered_df

@st.cache_data
def get_map_data(filtered_df):
    """Prepare the map data with latitude and longitude."""
    map_data = filtered_df[['geolocation_lat', 'geolocation_lng']].rename(columns={
        'geolocation_lat': 'latitude',
        'geolocation_lng': 'longitude'
    })
    return map_data


