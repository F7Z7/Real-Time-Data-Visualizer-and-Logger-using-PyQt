import csv,os
def logg_csv(graph_widget, directory: str,signal_name:str):
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        x_data,y_data = graph_widget.get_data()

    except AttributeError:
        print(f"No such data is available in the curve for signal {signal_name}")
        return

    file_path=os.path.join(directory,f"{signal_name}.csv")

    with open(file_path,'w',newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        headers=["Time (s)","Amplitude"]
        csv_writer.writerow(headers)

        for x, y in zip(x_data, y_data):
            csv_writer.writerow([x, y])

        print(f"✅ Logged '{signal_name}' to {file_path}")

    pass

def logg_binary():
    pass