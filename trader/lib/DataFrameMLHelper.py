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

    # convert format:
    # data = [[0.39777934 0.        ]
    #         [0.39751439 0.1981421 ]
    #         [0.39841926 0.35665894]
    #         ...
    # output: col1       col2
    #         0.39777934 0.0
    #         0.39751439 0.1981421
    #         0.39841926 0.35665894
    #         ...
    def convert_np_columns_to_df(self, data):
        df = pd.DataFrame(data, index=range(data.shape[0]),
                          columns=range(data.shape[1]))
        return df

    def series_to_supervised(self, data, n_in=1, n_out=1, dropnan=True):
        """
        Frame a time series as a supervised learning dataset.
        Arguments:
            data: Sequence of observations as a list or NumPy array.
            n_in: Number of lag observations as input (X).
            n_out: Number of observations as output (y).
            dropnan: Boolean whether or not to drop rows with NaN values.
        Returns:
            Pandas DataFrame of series framed for supervised learning.
        """
        n_vars = 1 if type(data) is list else data.shape[1]
        df = pd.DataFrame(data)
        cols, names = list(), list()
        # input sequence (t-n, ... t-1)
        for i in range(n_in, 0, -1):
            cols.append(df.shift(i))
            names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
        # forecast sequence (t, t+1, ... t+n)
        for i in range(0, n_out):
            cols.append(df.shift(-i))
            if i == 0:
                names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
            else:
                names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
        # put it all together
        agg = pd.concat(cols, axis=1)
        agg.columns = names
        # drop rows with NaN values
        if dropnan:
            agg.dropna(inplace=True)
        return agg
