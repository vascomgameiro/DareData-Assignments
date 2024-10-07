"""
This module cleans and transforms life expectancy data for a specified country.
"""

import argparse
import re
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).parents[1]
PACKAGE_DIR = PROJECT_DIR / "life_expectancy"
OUTPUT_DIR = PACKAGE_DIR / "data"


def clean_value(value: str) -> str:
    """Clean non-numeric characters from a string, keeping only digits, minus signs, and periods."""
    return re.sub(r"[^\d.-]", "", str(value))


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the life expectancy data by handling non-numeric values and dropping NaNs in 'value'."""
    df_cleaned = (
        df.assign(
            year=lambda df: pd.to_numeric(df["year"], errors="coerce").astype("Int64"),
            value=lambda df: pd.to_numeric(df["value"].apply(clean_value), errors="coerce"),
        ).dropna(subset=["value"])  # Drop rows with NaN in 'value' column after cleaning
    )
    return df_cleaned


def transform_df(df: pd.DataFrame, country: str) -> pd.DataFrame:
    """Transform the cleaned life expectancy data, splitting columns and filtering for the specified country."""
    df_transformed = (
        df.assign(
            unit=lambda df: df["unit,sex,age,geo\\time"].str.split(",", expand=True)[0],
            sex=lambda df: df["unit,sex,age,geo\\time"].str.split(",", expand=True)[1],
            age=lambda df: df["unit,sex,age,geo\\time"].str.split(",", expand=True)[2],
            region=lambda df: df["unit,sex,age,geo\\time"].str.split(",", expand=True)[3],
        )
        .drop(columns=["unit,sex,age,geo\\time"])  # Drop the original combined column
        .query(f'region == "{country}"')  # Filter for the specified country
    )
    return df_transformed


def clean_data(
    input_filename: str = "eu_life_expectancy_raw.tsv",
    output_filename: str = "pt_life_expectancy.csv",
    country: str = "PT",
) -> None:
    """Read, clean, and transform life expectancy data, saving the output as a CSV file."""

    input_file = OUTPUT_DIR / input_filename
    output_file = OUTPUT_DIR / output_filename

    # Read the raw data
    df = pd.read_csv(input_file, sep="\t")

    # Melt the data from wide to long format
    df_melted = df.melt(id_vars=["unit,sex,age,geo\\time"], var_name="year", value_name="value")

    # Clean and transform the data
    df = clean_df(df_melted)
    df = transform_df(df, country)
    df = df.loc[:, ["unit", "sex", "age", "region", "year", "value"]]

    # Save the final DataFrame to a CSV file
    df.to_csv(output_file, index=False)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Clean and transform life expectancy data for a specified country.")
    parser.add_argument("--country", type=str, default="PT", help="Country code to filter the data (default: PT)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(args.country)
    clean_data(country=args.country)
