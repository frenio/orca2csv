#!/usr/bin/env python

"""thermodata_orca_to_csv.py: Extracts thermochemistry data from an Orca output and writes them into a csv file."""

import os
import sys
import re
import csv
from pprint import pprint


def find_all(filename, path):
    """Returns all files called <filename> in <path>."""
    result = []
    for root, dirs, files in os.walk(path):
        if filename in files:
            result.append(os.path.join(root, filename))
    return result

def extract_vibrations(path_to_file):
    """Returns a dictionary of vibrational frequencies."""
    vib_dict = {}
    check = True
    vib_nr = 0
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    while check:
        expr = f"VIBRATIONAL FREQUENCIES(.*\n)+\s+{vib_nr}\:\s+(\-*\d+\.\d+)\s+(.*\n)+NORMAL MODES"
        try:
            vibration = re.search(expr, read_data).group(2)
            vib_dict[vib_nr] = round(float(vibration), 2)
            vib_nr += 1
        except:
            vib_imag = [i for i in vib_dict.values() if i < 0.00]
            vib_real = [i for i in vib_dict.values() if i > 0.00]
            print(f"Found {len(vib_real)} vibrations and {len(vib_imag)} imaginary frequencies.")
            check = False
    return vib_dict

def extract_vib_int(path_to_file):
    """Returns a list of tuples of vibrations and their IR intensities."""
    vib_dict = extract_vibrations(path_to_file)
    vib_dict = {k:vib_dict[k] for k in vib_dict.keys() if vib_dict[k] > 0.0}
    if 5 in set(vib_dict.keys()):
        print("Molecule is non-linear")
    elif 6 in set(vib_dict.keys()): 
        print("Molecule is non-linear")
    else:
        print("Structure is not a minimum")
    with open(path_to_file) as f:
        read_data = f.read()
    for key in vib_dict:
        expr = f"IR SPECTRUM(.*\n)+\s+{key}\:\s+{vib_dict[key]:.2f}\s+(\d+.\d+)\s+(.*\n)+The first frequency"
        intensity = re.search(expr, read_data).group(2)
        vib_dict[key] = (vib_dict[key], round(float(intensity), 2)) 
    return vib_dict

def extract_description(path_to_file):
    """Returns the description of the calculation with spaces replaced by underscores."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        description = re.search("NAME = .*\n.*#\s(.*)", read_data).group(1)
        description = description.strip()
        description = description.replace(' ', '_')
    except:
        print("Warning: No description found.")
        description = ''
    return description

def extract_method(path_to_file):
    """Returns a string - the calculation method."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        method = re.search("!\s[RU][KH][SF]\s([\w()]+)", read_data).group(1)
    except:
        print("Warning: Method not found.")
        method = ''
    return method

def extract_basis_set(path_to_file):
    """Returns a string - the basis set used for the calculation."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        basis_set = re.search("!\s[RU][KH][SF]\s[\w()]+\s([-\w]+)", read_data).group(1)
    except:
        print("Warning: Basis set not found.")
        basis_set = ''
    return basis_set

def extract_charge(path_to_file):
    """Returns an integer - the charge of the molecule."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        charge = re.search("\*\sxyz\s([-+\w]+)", read_data).group(1)
        charge = int(charge)
    except:
        print("Warning: Charge not found.")
        charge = None
    return charge

def extract_multiplicity(path_to_file):
    """Returns an integer - the multiplicity of the molecule."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        multiplicity = re.search("\*\sxyz\s[-+\w]+\s(\d)", read_data).group(1)
        multiplicity = int(multiplicity)
    except:
        print("Warning: Multiplicity not found.")
        multiplicity = None
    return multiplicity

def check_minimum(path_to_file):
    """Returns a boolean value telling whether the structure is or is not a minimum."""
    vib_dict = extract_vibrations(path_to_file)
    vib_imag = [i for i in vib_dict.values() if i < 0.00]
    if vib_imag == []:
        is_minimum = True
        print("No imaginary frequencies found. Structure is a minimum.")
    else:
        is_minimum = False
        print(f"{len(vib_imag)} imaginary frequencies found. Structure is not a minimum.")
    return is_minimum

def extract_electronic_energy(path_to_file):
    """Returns a float - the electronic energy of the atom or molecule."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    if "Single Point Calculation" in read_data:
        try:
            elec_en = re.search("FINAL SINGLE POINT ENERGY\s+(\-\d+\.\d+)", read_data).group(1)
            elec_en = float(elec_en)
        except:
            print("Warning: Electronic energy not found.")
            elec_en = None
    else:    
        try:
            elec_en = re.search("Electronic energy\s+\.\.\.\s+(\-\d+\.\d+)", read_data).group(1)
            elec_en = float(elec_en)
        except:
            print("Warning: Electronic energy not found.")
            elec_en = None
    return elec_en

def extract_zero_point_energy(path_to_file):
    """Returns a float - the zero point energy of the molecule."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        zero_point_en = re.search("Zero point energy\s+\.\.\.\s+(\d\.\d+)", read_data).group(1)
        zero_point_en = float(zero_point_en)
    except:
        print("Warning: Zero point energy not found.")
        zero_point_en = None
    return zero_point_en

def extract_inner_energy(path_to_file, temp = 298.15):
    """Returns a float - the inner energy at the temperature specified. Default temperature is 298.15 K."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        U = re.search(f"THERMOCHEMISTRY AT {temp:.2f}K(.*\n)+INNER ENERGY(.*\n)+Total thermal energy\s+(\-\d+\.\d+)", \
            read_data).group(3)
        U = float(U)
    except:
        print(f"Warning: Inner energy at {temp} K not found.")
        U = None
    return U

def extract_enthalpy(path_to_file, temp = 298.15):
    """Returns a float - the enthalpy at the temperature specified. Default temperature is 298.15 K."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        H = re.search(f"THERMOCHEMISTRY AT {temp:.2f}K(.*\n)+ENTHALPY(.*\n)+Total Enthalpy\s+\.*\s+(\-\d+\.\d+)", \
            read_data).group(3)
        H = float(H)
    except:
        print(f"Warning: Enthalpy at {temp} K not found.")
        H = None
    return H

def extract_entropy(path_to_file, temp = 298.15):
    """Returns a float - the entropy at the temperature specified. Default temperature is 298.15 K."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        S = re.search(f"THERMOCHEMISTRY AT {temp:.2f}K(.*\n)+ENTROPY(.*\n)+Final entropy term\s+\.*\s+(\d+\.\d+)", \
            read_data).group(3)
        S = float(S)
    except:
        print(f"Warning: Entropy at {temp} K not found.")
        S = None
    return S

def extract_gibbs_free_enthalpy(path_to_file, temp = 298.15):
    """Returns a float - the Gibbs free enthalpy at the temperature specified. Default temperature is 298.15 K."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        G = re.search\
            (f"THERMOCHEMISTRY AT {temp:.2f}K(.*\n)+GIBBS FREE ENTHALPY(.*\n)+Final Gibbs free enthalpy\s+\.*\s+(\-\d+\.\d+)",\
            read_data).group(3)
        G = float(G)
    except:
        print(f"Warning: Gibbs free enthalpy at {temp} K not found.")
        G = None
    return G

def extract_orca_version(path_to_file):
    """Returns a string of the Orca version used for the calculation."""
    with open(path_to_file, 'r') as f:
        read_data = f.read()
    try:
        version = re.search("Program Version (\d(\.\d)+)\s*-\s*RELEASE", read_data).group(1)
        version = f"Orca_{version}"
    except:
        print("Warning: Orca version not found.")
        version = ''
    return version

def extract_thermo_data(path_to_file, temp = 298.15):
    """Returns a dictionary of relevant thermochemistry data at the temperature specified. Default temperature is 298.15 K."""
    thermo_dict = {'description' : extract_description(path_to_file),
                   'method' : extract_method(path_to_file),
                   'basis_set' : extract_basis_set(path_to_file),
                   'is_ion' : bool(extract_charge(path_to_file)), 
                   'charge' : extract_charge(path_to_file), 
                   'multiplicity' : extract_multiplicity(path_to_file),
                   'is_minimum' : check_minimum(path_to_file),
                   'elec_en' : extract_electronic_energy(path_to_file),
                   'zero_point_en' : extract_zero_point_energy(path_to_file),
                   f'U{int(temp)}K' : extract_inner_energy(path_to_file, temp),
                   f'H{int(temp)}K' : extract_enthalpy(path_to_file, temp),
                   f'S{int(temp)}K' : extract_entropy(path_to_file, temp),
                   f'G{int(temp)}K' : extract_gibbs_free_enthalpy(path_to_file, temp),
                   'version' : extract_orca_version(path_to_file)}
    return thermo_dict

def collect_data(list_of_files, temp = 298.15):
    """Returns a list of dictionaries with thermochemistry data found 
    in all files with the specified name in the directory specified."""
    data_list = []
    for item in list_of_files:
        print()
        print(item)
        data_list.append(extract_thermo_data(item, temp))
        print()
    return data_list

def convert_data_to_csv(data_list, csv_file = 'thermodata.csv'):
    """Translates a list of dictionaries into a csv-file."""
    if os.path.isfile(csv_file):
        csv_columns = list(data_list[0].keys())
        with open(csv_file, 'r') as csvfile:
            header = next(csv.reader(csvfile))
        if header == csv_columns:
            with open(csv_file, 'a') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames = csv_columns)
                for data in data_list:
                    writer.writerow(data)
        else:
            print()
            print("Data not compatible with existing file:")
            print(header)
            print("does not match with")
            print(csv_columns)
            print()
    else:
        csv_columns = list(data_list[0].keys())
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = csv_columns)
            writer.writeheader()
            for data in data_list:
                writer.writerow(data)



if __name__ == "__main__":
    filename = sys.argv[1]
    path = sys.argv[2]
    try:
        temp = float(sys.argv[3])
    except:
        print()
        print("No temperature specified. Using default tepmerature (298.15 K).")
        temp = 298.15
    list_of_files = find_all(filename, path)
    data_list = collect_data(list_of_files, temp)
    csv_file = f'thermodata_at_{int(temp)}K.csv'
    print()
    pprint(data_list, sort_dicts = False)
    convert_data_to_csv(data_list, csv_file)
    print()

