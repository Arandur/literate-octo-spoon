#!/usr/bin/python2

import csv
import re

def get_data (rows) :
    data = []
    i = 0

    while (i != len (rows)):
        datum, i = get_next_datum (rows, i)

        if datum is not None:
            data.append (datum)

    return data

def get_next_datum (rows, i) :
    datum_name, j = get_next_datum_name (rows, i)
    datum_vals, k = get_next_datum_vals (rows, j)

    if datum_name is not None and datum_vals is not None:
        return (datum_name, datum_vals), k

    return None, len (rows)

def get_next_datum_name (rows, i) :
    for row in rows[i:]:
        if "Sample" in row:
            col = row.index ("Sample")
            return rows[i + 1][col], i + 2

    return None, len (rows)

def get_next_datum_vals (rows, i):
    for j, row in enumerate (rows[i:]) :
        if "R.T." in row and "Area" in row:
            col_k = row.index ("R.T.")
            col_v = row.index ("Area")

            vals = {}
            
            for m, row in enumerate (rows[i + j + 1:]) :
                try :
                    k = float (row[col_k])
                    v = int   (row[col_v])
                    vals[k] = v # to avoid fp errors
                except ValueError :
                    return vals, i + j + 1 + m

            return vals, len (rows)

    return None, len (rows)

def name_splitter (pattern) :
    def split_name (name) :
        try :
            return re.match (pattern, name).groupdict ()
        except AttributeError :
            from sys import stderr
            print >> stderr, "Format error in sample label:", name
            print >> stderr, "Data will be used without any label"

            return {}

    return split_name

def generate_output_vals (data) :
    name_labels = [ "ColID", "ColType", "Week", "Vial" ]
    pattern = re.compile ( \
            r"(?P<ColID>\w+)\s+(?P<ColType>\w+)\s+(?P<Week>\w+\s+\d+)\s+V(?P<Vial>\d)")
    split_name = name_splitter (pattern)

    output_vals = [dict (vals.items () + split_name (name).items ()) \
                   for name, vals in data]
    output_labels = \
            name_labels + \
            sorted(reduce(set.union, (set (vals.keys ()) for _, vals in data)))

    return output_labels, output_vals

if __name__ == "__main__" :
    import sys

    if len (sys.argv) != 3:
        in_path = raw_input ("Input file path: ")
        out_path = raw_input ("Output file path [out.csv]: ")
        if out_path == "" :
            out_path = "out.csv"
    else :
        in_path = sys.argv[1]
        out_path = sys.argv[2]

    with open (in_path, "r") as f:
        data = get_data (list (csv.reader (f)))

    with open (out_path, "w") as f:
        out_labels, out_vals = generate_output_vals (data)
        writer = csv.DictWriter (f, fieldnames = out_labels)
        writer.writeheader ()
        for val in out_vals :
            writer.writerow (val)

    print "Successfully wrote to", out_path
    print "Press ENTER to close this window"
