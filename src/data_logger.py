import csv
import os

class DataLogger:
    def __init__(self, curve, signal_name, directory):
        self.curve = curve
        self.signal_name = signal_name
        self.directory = directory

    def logg_csv(self):
        if not self.curve:
            print("No curve to log.")
            return

        try:
            x_data, y_data = self.curve.getData()
            if x_data is None or y_data is None:
                print("Curve data is empty.")
                return
        except AttributeError:
            print(f" No such data is available in the curve for signal '{self.signal_name}'")
            return

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        file_path = os.path.join(self.directory, f"{self.signal_name}.csv")
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x, y in zip(x_data, y_data):
                writer.writerow([x, y])

        print(f"✅ Logged '{self.signal_name}' to {file_path}")

    def logg_binary(self):
        # Placeholder
        pass
