import csv

def create_csv():
    runs = [387474, 387506]
    dataset = "/StreamExpress/Run2024J-Express-v1/DQMIO/"
    output_file = "runlist.csv"

    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["run", "dataset"])
        for run in runs:
            writer.writerow([run, dataset])

    print(f"File '{output_file}' creato con successo!")

if __name__ == "__main__":
    create_csv()
