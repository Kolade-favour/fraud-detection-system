import mysql.connector
from mysql.connector import Error
import pandas as pd
from pathlib import Path

from src.database.db_config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME 
)

def get_server_connection():
    """
    Establishes a connection to the MySQL server.

    Returns:
        mysql.connector.connection.MySQLConnection: A connection object to the MySQL server.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL server: {e}")
        return None



def create_database():
    """
    Creates the database if it does not exist.
    """
    connection = get_server_connection()
    if connection is None:
        print("Failed to connect to the MySQL server. Cannot create database.")
        return False

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                       "CHARACTER SET utf8mb4 "
                       "COLLATE utf8mb4_unicode_ci;")
        print(f"Database '{DB_NAME}' is ready.")
        return True

    except Error as e:
        print(f"Error while creating database: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_database_connection():
    """
    Establishes a connection to the specified MySQL database.

    Returns:
        mysql.connector.connection.MySQLConnection: A connection object to the MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL database: {e}")


        return None


def initialize_simulator_checkpoint(
    simulator_name="fraud_transaction_simulator"
):
    """
    Create the simulator checkpoint if it does not already exist.

    A new simulator starts from source_record_id = 0.
    Existing checkpoints are preserved.
    """

    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Could not connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT IGNORE INTO simulator_state (
                simulator_name,
                last_source_record_id
            )
            VALUES (%s, 0)
        """

        cursor.execute(query, (simulator_name,))
        connection.commit()

        return True

    except Error as e:
        connection.rollback()
        raise RuntimeError(
            f"Could not initialize simulator checkpoint: {e}"
        ) from e

    finally:
        if cursor:
            cursor.close()

        connection.close()


def get_simulator_checkpoint(
    simulator_name="fraud_transaction_simulator"
):
    """
    Retrieve the last successfully registered source record ID.
    """

    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Could not connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT last_source_record_id
            FROM simulator_state
            WHERE simulator_name = %s
        """

        cursor.execute(query, (simulator_name,))
        result = cursor.fetchone()

        if result is None:
            raise ValueError(
                "Simulator checkpoint does not exist. "
                "Initialize it first."
            )

        return result[0]

    except Error as e:
        raise RuntimeError(
            f"Could not retrieve simulator checkpoint: {e}"
        ) from e

    finally:
        if cursor:
            cursor.close()

        connection.close()


def create_tables():
    """
    Create all application tables if they do not already exist.
    """

    connection = get_database_connection()

    if connection is None:
        print("Failed to connect to the application database.")
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        # Generate the PCA feature columns V1 to V28
        pca_columns = ",\n".join(
            [f"`V{i}` DOUBLE NOT NULL" for i in range(1, 29)]
        )

        # 1. Original ULB dataset
        raw_transactions_table = f"""
        CREATE TABLE IF NOT EXISTS raw_transactions (
            source_record_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            `Time` DOUBLE NOT NULL,
            {pca_columns},
            `Amount` DOUBLE NOT NULL,
            `Class` TINYINT NOT NULL,
            CONSTRAINT chk_raw_class CHECK (`Class` IN (0, 1))
        ) ENGINE=InnoDB;
        """

        # 2. Simulator events
        # 2. Simulator events
        simulated_transactions_table = """
        CREATE TABLE IF NOT EXISTS simulated_transactions (
            simulation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            source_record_id BIGINT NOT NULL,
            replayed_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',

            updated_at DATETIME(6)
                NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                ON UPDATE CURRENT_TIMESTAMP(6),

            processed_at DATETIME(6) NULL,

            CONSTRAINT fk_simulation_source
                FOREIGN KEY (source_record_id)
                REFERENCES raw_transactions(source_record_id)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT,

            INDEX idx_simulation_source (source_record_id),
            INDEX idx_simulation_status (processing_status)
        ) ENGINE=InnoDB;
        """

        # 3. Model prediction results
        prediction_results_table = """
        CREATE TABLE IF NOT EXISTS prediction_results (
            prediction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            simulation_id BIGINT NOT NULL,
            model_version VARCHAR(100) NOT NULL,
            prediction_timestamp DATETIME(6)
                NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

            legitimate_probability DOUBLE NOT NULL,
            fraud_probability DOUBLE NOT NULL,
            decision_threshold_used DOUBLE NOT NULL,
            predicted_class TINYINT NOT NULL,
            risk_level VARCHAR(20)  NULL,

            top_features JSON,
            shap_values JSON,
            explanation TEXT,

            CONSTRAINT fk_prediction_simulation
                FOREIGN KEY (simulation_id)
                REFERENCES simulated_transactions(simulation_id)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT,

            CONSTRAINT chk_prediction_class
                CHECK (predicted_class IN (0, 1)),

            CONSTRAINT chk_prediction_probabilities
                CHECK (
                    legitimate_probability BETWEEN 0 AND 1
                    AND fraud_probability BETWEEN 0 AND 1
                ),

            CONSTRAINT chk_decision_threshold
                CHECK (decision_threshold_used BETWEEN 0 AND 1),

            INDEX idx_prediction_simulation (simulation_id),
            INDEX idx_prediction_class (predicted_class),
            INDEX idx_prediction_risk (risk_level),
            INDEX idx_prediction_timestamp (prediction_timestamp)
        ) ENGINE=InnoDB;
        """

        # 4. Analyst decisions
        analyst_decisions_table = """
        CREATE TABLE IF NOT EXISTS analyst_decisions (
            decision_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            prediction_id BIGINT NOT NULL,
            analyst_outcome VARCHAR(30) NOT NULL,
            notes TEXT,
            reviewer VARCHAR(100),
            decision_timestamp DATETIME(6)
                NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

            CONSTRAINT fk_decision_prediction
                FOREIGN KEY (prediction_id)
                REFERENCES prediction_results(prediction_id)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT,

            INDEX idx_decision_prediction (prediction_id),
            INDEX idx_decision_outcome (analyst_outcome),
            INDEX idx_decision_timestamp (decision_timestamp)
        ) ENGINE=InnoDB;
        """

                # 5. Simulator execution state
        simulator_state_table = """
        CREATE TABLE IF NOT EXISTS simulator_state (
            simulator_name VARCHAR(50) PRIMARY KEY,
            last_source_record_id BIGINT NOT NULL DEFAULT 0,
            updated_at DATETIME(6)
                NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                ON UPDATE CURRENT_TIMESTAMP(6)
        ) ENGINE=InnoDB;
        """

        # Execute table creation in dependency order
        tables = [
            raw_transactions_table,
            simulated_transactions_table,
            prediction_results_table,
            analyst_decisions_table,
            simulator_state_table
        ]

        for table_sql in tables:
            cursor.execute(table_sql)

        connection.commit()

        print("All five database tables are ready.")
        return True

    except Error as e:
        connection.rollback()
        print(f"Error while creating tables: {e}")
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()



def load_raw_transactions(batch_size=10000):
    """
    Load the original ULB credit card dataset into raw_transactions.

    Assigns stable source_record_id values based on CSV row position.
    Uses INSERT IGNORE to make repeated imports safe.
    """

    csv_path = Path("data/raw/creditcard.csv")

    if not csv_path.exists():
        print(f"Dataset not found: {csv_path}")
        return False

    connection = get_database_connection()

    if connection is None:
        print("Failed to connect to the application database.")
        return False

    cursor = None

    expected_columns = (
        ["Time"]
        + [f"V{i}" for i in range(1, 29)]
        + ["Amount", "Class"]
    )

    insert_columns = ["source_record_id"] + expected_columns

    column_names = ", ".join(
        f"`{column}`" for column in insert_columns
    )

    placeholders = ", ".join(["%s"] * len(insert_columns))

    insert_query = f"""
        INSERT IGNORE INTO raw_transactions ({column_names})
        VALUES ({placeholders})
    """

    next_source_id = 1
    total_processed = 0
    total_inserted = 0

    try:
        cursor = connection.cursor()

        # Read the CSV in manageable batches
        for chunk in pd.read_csv(csv_path, chunksize=batch_size):

            # Validate the dataset structure
            if chunk.columns.tolist() != expected_columns:
                raise ValueError(
                    "Dataset columns do not match the expected ULB schema."
                )

            # Check for missing values
            if chunk.isnull().values.any():
                raise ValueError(
                    "Dataset contains missing values."
                )

            # Validate target labels
            if not chunk["Class"].isin([0, 1]).all():
                raise ValueError(
                    "Class column contains invalid target values."
                )

            # Generate stable IDs from original CSV row positions
            records = [
                (next_source_id + index, *row)
                for index, row in enumerate(
                    chunk.itertuples(index=False, name=None)
                )
            ]

            cursor.executemany(insert_query, records)
            connection.commit()

            inserted = cursor.rowcount

            total_processed += len(records)
            total_inserted += inserted
            next_source_id += len(records)

            print(
                f"Processed: {total_processed:,} | "
                f"Inserted: {total_inserted:,}"
            )

        # Verify the final database record count
        cursor.execute(
            "SELECT COUNT(*) FROM raw_transactions"
        )

        database_count = cursor.fetchone()[0]

        print("\nRaw dataset import completed.")
        print(f"Rows processed: {total_processed:,}")
        print(f"New rows inserted: {total_inserted:,}")
        print(f"Total records in database: {database_count:,}")

        return True

    except (Error, ValueError, Exception) as e:
        connection.rollback()
        print(f"Dataset import error: {e}")
        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()

        