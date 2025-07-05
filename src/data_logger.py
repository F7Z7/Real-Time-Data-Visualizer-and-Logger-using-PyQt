import csv
import os
import struct
class DataLogger:
    def __init__(self, curve, signal_name, directory,max_file_size,new_file):
        self.curve = curve
        self.signal_name = signal_name
        self.directory = directory
        self.max_file_size = max_file_size
        self.new_file = new_file
        self.file_format="CSV" #default is csv


        #giving the files index to avoid duplicates
        self.file_index = 1
        self.file_path = self.get_file_path()

    def get_file_path(self):
        ext = "csv" if self.file_format == "csv" else "bin"
        if self.new_file:
            return os.path.join(self.directory, f"{self.signal_name}_{self.file_index}.{ext}")
        else:
            return os.path.join(self.directory, f"{self.signal_name}.{ext}")

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

        current_size=os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0
        #if not exits =write headert true
        write_header=current_size==0
        with open(self.file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(["Time (s)", "Amplitude"])

            for x, y in zip(x_data, y_data):
                row = [x, y]
                row_size = sum(len(str(val)) for val in row) + 2 #checking size

                if current_size +row_size > self.max_file_size: #checking if its inside the limits
                    if self.new_file:
                        self.file_index += 1 #increment for next file
                        self.file_path = self.get_file_path()
                        current_size = 0

                        with open(self.file_path, 'a', newline='') as new_csvfile:
                            new_writer = csv.writer(new_csvfile)
                            new_writer.writerow(["Time (s)", "Amplitude"])
                            new_writer.writerow(row)
                        current_size += row_size
                    else:
                        print("File size exceeds max_file_size limit. Logging stopped")
                else:
                    writer.writerow(row)
                    current_size += row_size



    def logg_binary(self):
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

        self.file_path = os.path.join(self.directory, f"{self.signal_name}.bin")
        with open(self.file_path, 'ab') as binfile:
            for x, y in zip(x_data, y_data):
                binfile.write(struct.pack('dd', x, y)) #dd indicates flota64

