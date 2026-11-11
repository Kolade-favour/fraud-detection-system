import time

from src.simulator import run_simulator
from src.inference import run_inference


def start_scheduler(interval_seconds=60):

    print("Fraud detection scheduler started.")
    print(f"Waiting interval: {interval_seconds} seconds")

    try:
        while True:

            print("\nStarting transaction simulation...")

            try:
                simulator_results = run_simulator(
                    max_transactions=1000,
                    batch_size=100,
                    max_runtime_seconds=300
                )
                print("Simulation completed:", simulator_results)

            except Exception as e:
                print(f"Simulation failed: {e}")

            print("\nStarting inference processing...")

            try:
                inference_results = run_inference(
                    max_transactions=1000,
                    batch_size=100,
                    max_runtime_seconds=300
                )
                print("Inference completed:", inference_results)

            except Exception as e:
                print(f"Inference failed: {e}")

            print(f"\nNext cycle in {interval_seconds} seconds.")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")


if __name__ == "__main__":
    start_scheduler()