def get_positive(data_frame, column_name):
    """
    Query given data frame for positive values, including zero

    :param data_frame: Pandas data frame to query
    :param column_name: column name to filter values by
    :return: DataFrame view
    """
    return data_frame.query(f'{column_name} >= 0')


def get_negative(data_frame, column_name):
    """
    Query given data frame for negative values, including null or NaN.

    From StackOverflow: Utilize the fact that np.nan != np.nan

    :param data_frame: Pandas data frame to query
    :param column_name: column name to filter values by
    :return: DataFrame view
    """
    return data_frame.query(
        f'({column_name} < 0) or ({column_name} != {column_name})'
    )


def get_no_data(data_frame, column_name):
    """
    Query given data frame for null or NaN.

    :param data_frame: Pandas data frame to query
    :param column_name: column name to filter values by
    :return: DataFrame view
    """
    return data_frame.query(f'{column_name} != {column_name}'
    )
