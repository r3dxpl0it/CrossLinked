# CrossLinked (Forked) 

Forked Version Changes : 

  Done : 
    - Does not generate mail and Generate a json file of employee and linkedin adress
    - Only Uses *Bing*
    - More Result than original version
  TODO : 
    - add tor capabilies

Original Version : https://github.com/m8r0wn/CrossLinked

## Setup
```bash
git clone https://github.com/r3dxpl0it/CrossLinked
cd crosslinked
pip3 install -r requirements.txt
```

## Examples
```bash
python3 crosslinked.py company_name -v -o out_put_file.json
```

## Usage
```
positional arguments:
  company_name  Target company name

optional arguments:
  -h, --help    show this help message and exit
  -t TIMEOUT    Timeout [seconds] for search threads (Default: 25)
  -j JITTER     Jitter for scraping evasion (Default: 0)
  -o OUTFILE    Change name of output file (default: names.txt
  -s, --safe    Only parse names with company in title (Reduces false positives)
  -v            Show names and titles recovered after enumeration

```

```
