# orca2csv
A collection of python scripts that extract data from Orca (a quantum chemistry program package) output files and write the data into a csv file. The python scripts are meant to help chemists extract and analyze computational data that is relevant to them.

## thermodata_orca_to_csv.py
Apart from functions to extract thermochemistry data the script also contains functions to extract vibrational frequencies from an Orca output file. If used as "__main__" use as follows:

$ python thermodata_orca_to_csv.py <filename.out> <path_to_directory> <temperature>

The script looks for all files with the name "filename.out" in "path_to_directory", extracts the data that was calculated at the specified "temperature" (in K), and creates a csv that contains the extracted data. One row for each file.

The way I use Orca, output files always have the same name. That way this script allows me to extract the thermochemistry data of all output files in a given directory.
