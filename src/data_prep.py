import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from src.database.database import get_database_connection

RANDOM_STATE = 42

def load_and_clean_data():
    """
    Load and clean the transaction data from the database.

    Returns:
        pd.DataFrame: Cleaned transaction data.
    """
    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Failed to connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor()

        # Retrieve original datasets columns
        # Source_record_id is excluded because it is not a model feature
        columns = ["`Time`"] 
        columns += [f"`V{i}`" for i in range(1, 29)]
        columns += ["`Amount`", "`Class`"]

        query = f"""
            SELECT {', '.join(columns)}
            FROM raw_transactions
        """

        cursor.execute(query)
        records = cursor.fetchall()

        # Convert records to a pandas DataFrame
        df = pd.DataFrame(records, 
                          columns=["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"])

    except Exception as e:
        raise RuntimeError(f"Error occurred while fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        connection.close()


    # Record initial dataset size
    initial_size = len(df)

    # Remove duplicates transections records
    df = df.drop_duplicates().reset_index(drop=True)

    duplicates_removed = initial_size - len(df)

    # validate missing values
    missing_values = df.isnull().sum().sum()

    if missing_values > 0:
        raise ValueError(f"Data contains {missing_values} missing values. Please handle them before proceeding.")

    # validate target labels
    if not df['Class'].isin([0, 1]).all():
        raise ValueError("Target labels must be binary (0 or 1).")

    print(f"Original records: {initial_size:,}")
    print(f"Duplicates removed: {duplicates_removed:,}")
    print(f"Cleaned records: {len(df):,}")
    print(f"Missing values: {missing_values}")

    print("\nClass distribution:")
    print(df["Class"].value_counts())


    return df


def prepare_train_test_data(df):
    """
    separate  features and target, then perform
    a stratified 80/20 train-test split.
    """

    X = df.drop(columns=["Class"])
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    print("\nTraining data:", X_train.shape)
    print("Testing data:", X_test.shape)

    print("\nTraining class distribution:")
    print(y_train.value_counts(normalize=True))

    print("\nTesting class distribution:")
    print(y_test.value_counts(normalize=True))

    return X_train, X_test, y_train, y_test
