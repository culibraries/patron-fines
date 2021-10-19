# Patron Fines (Sierra)

Patron Fines transform code for the innopac charge files from Sierra.

## Requirements

1. Python3
2. Pandas

## Installation

```sh
python3 -m venv <dir> 
. <dir>/bin/activate 
pip install -r requirements.txt
```
## Operation
```sh
./transform innopac.charge.09-08-2021,innopac.charge.09-15-2021 out.csv
```
## Arguments

1. comma separated input files
1. Outfile