# helper class for processing pandas DataFrame for use with Machine Learning (ML)
import pandas as pd


class DataFrameMLHelper(object):
    def __init__(self, df=None):
        self.df = df

    def set_dataframe(self, df):
        self.df = df

    def get_dataframe(self):
        return self.df

    # get DataFrame only with columns specified
    def get_dataframe_with_columns(self, columns, df=None):
        if not df:
            df = self.df
        return pd.DataFrame(df, columns=columns)

    # set internal DataFrame only with columns specified
    def set_dataframe_with_columns(self, columns, df=None):
        if df:
            self.df = df
        self.df = pd.DataFrame(self.df, columns=columns)

    # add feature to dataframe using indicator and return indicator *TODO*
    def add_feature_indicator(self, column_name, df=None):
        pass

    # split a column into count columns for train/test ML and return trainY if train is true
    def get_split_dataset_by_column(self, column_name, count, train=True, df=None):
        #if not df:
        #    df = self.df
        new_df = pd.DataFrame()
        if train:
            shift_start = 0
        else:
            shift_start = 1
        for shift in range(shift_start, count + shift_start):
            cname = "{}{}".format(column_name, shift)
            shift_end = -(count - shift)
            if shift_end:
                new_df[cname] = df[column_name].values[shift:shift_end]
            else:
                new_df[cname] = df[column_name].values[shift:]
        #df = df.drop(columns=column_name)
        return new_df
