#!/usr/bin/python2

# Copyright (C) 2016  J. Anthony Sterrett, Jr.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

def datum_keys_getter (key_labels) :
    def get_next_datum_keys (rows, i) :
        for row in rows[i:]:
            if all (k in row for k in key_labels) :
                cols = [row.index (k) for k in key_labels]
                return [rows[i + 1][col] for col in cols], i + 2

        return None, len (rows)

    return get_next_datum_keys

def datum_vals_getter (key_val_label, val_label) :
    def get_next_datum_vals (rows, i):
        for j, row in enumerate (rows[i:]) :
            if key_val_label in row and val_label in row :
                col_k = row.index (key_val_label)
                col_v = row.index (val_label)

                vals = {}
                
                for m, row in enumerate (rows[i + j + 1:]) :
                    try :
                        k = float (row[col_k])
                        vals[k] = row[col_v]
                    except ValueError :
                        return vals, i + j + 1 + m

                return vals, len (rows)

        return None, len (rows)

    return get_next_datum_vals

def get_next_datum (rows, i) :
    get_next_datum_keys = datum_keys_getter (["Sample", "Misc"])
    get_next_datum_vals = datum_vals_getter ("R.T.", "Area")

    datum_keys, j = get_next_datum_keys (rows, i)
    datum_vals, k = get_next_datum_vals (rows, j)

    if datum_keys is not None and datum_vals is not None:
        return (datum_keys, datum_vals), k

    return None, len (rows)

def generate_output_vals (data) :
    output_vals = [dict (vals.items () + zip (["Sample", "Misc"], keys)) \
                   for keys, vals in data]
    output_labels = \
            ["Sample", "Misc"] + \
            sorted(reduce(set.union, (set (vals.keys ()) for _, vals in data)))

    return output_labels, output_vals

if __name__ == "__main__" :
    import sys

    if len (sys.argv) == 1:
        in_path = raw_input ("Input file path: ")
        out_path = raw_input ("Output file path [out.csv]: ")
        if out_path == "" :
            out_path = "out.csv"
    elif len (sys.argv) == 2:
        in_path = sys.argv[1]
        out_path = "out.csv"
    else :
        in_path = sys.argv[1]
        out_path = sys.argv[2]

    with open (in_path, "rb") as f:
        data = get_data (list (csv.reader (f)))

    with open (out_path, "wb") as f:
        out_labels, out_vals = generate_output_vals (data)
        writer = csv.DictWriter (f, fieldnames = out_labels)
        writer.writeheader ()
        for val in out_vals :
            writer.writerow (val)

    print "Successfully wrote to", out_path
    raw_input ("Press ENTER to close this window")
