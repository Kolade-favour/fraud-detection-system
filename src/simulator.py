
from src.database.database import (
    get_database_connection,
    initialize_simulator_checkpoint,
    get_simulator_checkpoint
)

import time



def fetch_transactions(batch_size=1000, last_source_record_id=0):
    """
    Retrieve transactions from raw_transactions in batches,
    using source_record_id for pagination.
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Could not connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Select original transaction features
        columns = ["source_record_id", "`Time`"]
        columns += [f"`V{i}`" for i in range(1, 29)]
        columns += ["`Amount`"]

        column_names = ", ".join(columns)

        query = f"""
            SELECT {column_names}
            FROM raw_transactions
            WHERE source_record_id > %s
            ORDER BY source_record_id ASC
            LIMIT %s
        """

        cursor.execute(
            query,
            (last_source_record_id, batch_size)
        )

        transactions = cursor.fetchall()

        return transactions

    finally:
        if cursor:
            cursor.close()

        connection.close()




def register_simulation(
    source_record_id,
    simulator_name="fraud_transaction_simulator"
):
    """
    Register a simulation event and update the checkpoint
    within the same database transaction.

    Returns:
        int: Generated simulation_id if successful, otherwise None.
    """

    connection = get_database_connection()

    if connection is None:
        print("Could not connect to the database.")
        return None

    cursor = None

    try:
        cursor = connection.cursor()

        # 1. Retrieve and lock the current checkpoint
        checkpoint_query = """
            SELECT last_source_record_id
            FROM simulator_state
            WHERE simulator_name = %s
            FOR UPDATE
        """

        cursor.execute(checkpoint_query, (simulator_name,))
        result = cursor.fetchone()

        if result is None:
            raise ValueError("Simulator checkpoint does not exist.")

        last_source_record_id = result[0]

        # 2. Prevent duplicate or out-of-order registration
        if source_record_id <= last_source_record_id:
            raise ValueError(
                f"Source record {source_record_id} has already "
                "been registered or is behind the checkpoint."
            )

        # 3. Register the simulation event
        insert_query = """
            INSERT INTO simulated_transactions (source_record_id)
            VALUES (%s)
        """

        cursor.execute(insert_query, (source_record_id,))
        simulation_id = cursor.lastrowid

        # 4. Update the checkpoint
        update_query = """
            UPDATE simulator_state
            SET last_source_record_id = %s
            WHERE simulator_name = %s
        """

        cursor.execute(
            update_query,
            (source_record_id, simulator_name)
        )

        # 5. Commit both operations together
        connection.commit()

        return simulation_id

    except Exception as e:
        connection.rollback()
        print(f"Simulation registration error: {e}")
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()



def replay_transaction(transaction):
    """
    Register a transaction as a simulation event
    and return its features with the generated simulation_id.
    """

    source_record_id = transaction["source_record_id"]

    simulation_id = register_simulation(source_record_id)

    if simulation_id is None:
        return None

    # Combine the original transaction features with its simulation ID
    replayed_transaction = {
        **transaction,
        "simulation_id": simulation_id
    }

    return replayed_transaction


def reset_simulator_checkpoint(
    simulator_name="fraud_transaction_simulator"
):
    """
    Reset the simulator checkpoint to zero when the
    raw dataset has been exhausted.
    """

    connection = get_database_connection()

    if connection is None:
        raise ConnectionError("Could not connect to the database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            UPDATE simulator_state
            SET last_source_record_id = 0
            WHERE simulator_name = %s
        """

        cursor.execute(query, (simulator_name,))

        if cursor.rowcount == 0:
            raise ValueError("Simulator checkpoint was not found.")

        connection.commit()

        print("Dataset exhausted. Checkpoint reset to 0.")
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()

        connection.close()




def run_simulator(
    max_transactions=1000,
    batch_size=100,
    max_runtime_seconds=300
):
    """
    Run a bounded transaction replay simulation.

    Resumes from the saved checkpoint after interruption.
    Automatically restarts from the beginning when the
    raw dataset is exhausted.
    """

    # 1. Validate execution limits
    if max_transactions <= 0 or batch_size <= 0:
        raise ValueError(
            "Transaction limits must be greater than zero."
        )

    if max_runtime_seconds <= 0:
        raise ValueError(
            "Runtime must be greater than zero."
        )

    # 2. Initialize or retrieve checkpoint
    initialize_simulator_checkpoint()

    last_source_id = get_simulator_checkpoint()

    print(f"Resuming from source record ID: {last_source_id}")

    # 3. Initialize execution statistics
    start_timestamp = time.monotonic()

    records_attempted = 0
    events_registered = 0
    failed_events = 0
    replay_cycles = 0

    # 4. Main simulation loop
    while records_attempted < max_transactions:

        elapsed_time = time.monotonic() - start_timestamp

        if elapsed_time >= max_runtime_seconds:
            print("Maximum runtime reached.")
            break

        remaining = max_transactions - records_attempted
        current_batch_size = min(batch_size, remaining)

        # 5. Retrieve next batch
        transactions = fetch_transactions(
            batch_size=current_batch_size,
            last_source_record_id=last_source_id
        )

        # 6. Handle dataset exhaustion
        if not transactions:

            # Prevent repeatedly resetting an empty dataset
            if last_source_id == 0:
                print("Raw dataset is empty. Stopping simulation.")
                break

            print("Raw dataset exhausted.")

            try:
                reset_simulator_checkpoint()
                last_source_id = 0
                replay_cycles += 1

                print("Restarting replay from the first raw record.")

            except Exception as e:
                print(f"Checkpoint reset failed: {e}")
                break

            continue

        registration_failed = False

        # 7. Register transactions individually
        for transaction in transactions:

            elapsed_time = time.monotonic() - start_timestamp

            if elapsed_time >= max_runtime_seconds:
                print("Maximum runtime reached.")
                break

            source_record_id = transaction["source_record_id"]

            result = replay_transaction(transaction)

            records_attempted += 1

            if result is not None:

                events_registered += 1
                last_source_id = source_record_id

            else:

                failed_events += 1
                registration_failed = True

                print(
                    f"Registration failed for source record "
                    f"{source_record_id}"
                )

                break

        # 8. Display batch progress
        print(
            f"Attempted: {records_attempted} | "
            f"Registered: {events_registered} | "
            f"Failed: {failed_events} | "
            f"Checkpoint: {last_source_id}"
        )

        if registration_failed:
            print("Simulation stopped due to registration failure.")
            break

    # 9. Calculate runtime
    elapsed_time = time.monotonic() - start_timestamp

    # 10. Display execution summary
    print("\nSimulation execution completed.")
    print(f"Records attempted: {records_attempted}")
    print(f"Events registered: {events_registered}")
    print(f"Failed events: {failed_events}")
    print(f"Replay cycles started: {replay_cycles}")
    print(f"Last source record ID: {last_source_id}")
    print(f"Runtime: {elapsed_time:.2f} seconds")

    return {
        "records_attempted": records_attempted,
        "events_registered": events_registered,
        "failed_events": failed_events,
        "replay_cycles": replay_cycles,
        "elapsed_seconds": elapsed_time,
        "last_source_record_id": last_source_id
    }
