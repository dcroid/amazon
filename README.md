
<img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg">

#Parsing amazon product

**Install:**<br>
```pip install -r requirements.txt```

**Args for parsing Amazon product:**
```
python main.py --help
usage: main.py [-h] [--url URL] [--f F]

optional arguments:
  -h, --help  show this help message and exit
  --url URL   Amazon url category
  --f F       File name for save data
```

Example:
```
python main.py --url "https://www.amazon.it/s?k=COLGATE&rh=n%3A1571289031&dc&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1597410013&rnid=1640607031&ref=sr_nr_n_1"
```

Todo:
* Add proxy
* Add detect captha
