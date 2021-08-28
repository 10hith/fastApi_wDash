from pyspark.sql import functions as f
from pyspark.sql import DataFrame

def transform(self, f):
    """
    Method monkey patched into the DataFrame class.
    It enables to chain the transformations/functions passed as f
    Usage:  testDF.\
        transform(with_date_cols_casted).\
        transform(with_decimal_cols_casted).\
        transform(trim_columns(["col2", "col2"]))

    """
    return f(self)


DataFrame.transform = transform


def cleanup_col_name(col_name):
    str_w_space = ' '.join(col_name.split())
    str_w_underscore = str_w_space.replace(' ', '_' )
    return (col_name, str_w_underscore.lower())


def build_select_expr(cols_map):
    select_expr = [" `{}` as {}".format(x[0],x[1]) for x in cols_map]
    return select_expr


def with_std_column_names():
    """
    Conform all the columns to be stripped of all whitespaces lowercase
    Args:
        cols: list of columns

    Returns:
        Dataframe with specified columns converted
    """

    def inner(df):
        cols_map = [cleanup_col_name(x) for x in df.columns]
        select_expr=build_select_expr(cols_map)
        return df.selectExpr(select_expr)

    return inner


def with_sas_date_format_converted(col_names):
    """
    Convert date to standard date format: 	24JUL2020 to 2020-07-24
    Args:
        cols: list of columns

    Returns:
        Dataframe with specified columns converted
    """

    def inner(df):
        for col_name in col_names:
            df = df.withColumn(col_name, f.to_date(f.from_unixtime(f.unix_timestamp(col_name, 'ddMMMyyyy'))))
        return df

    return inner


def with_std_date_format(col_names):
    """
    Convert date to standard date format: 30/10/2019 to 2019-10-30
    Args:
        cols: list of columns

    Returns:
        Dataframe with specified columns converted
    """

    def inner(df):
        for col_name in col_names:
            df = df.withColumn(col_name, f.to_date(f.from_unixtime(f.unix_timestamp(col_name, 'dd/MM/yyyy'))))
        return df

    return inner


def with_zero_for_nulls(col_names):
    """
    Convert date to standard date format: 30/10/2019 to 2019-10-30
    Args:
        cols: list of columns

    Returns:
        Dataframe with specified columns converted
    """

    def inner(df):
        for col_name in col_names:
            df = df.withColumn(col_name, f.expr("COALESCE(CAST({} AS DOUBLE), 0.0)".format(col_name)))
        return df

    return inner


def with_avg_for_nulls(col_names):
    """
    Convert date to standard date format: 30/10/2019 to 2019-10-30
    Args:
        cols: list of columns

    Returns:
        Dataframe with specified columns converted
    """

    def inner(df):
        col_avg = df.select([f.avg(col).alias(col) for col in col_names]).collect()
        for col_name in col_names:
            df = df.withColumn(col_name, f.expr("COALESCE(CAST({} AS DOUBLE), {})".format(col_name, col_avg[0][col_name])))
        return df

    return inner