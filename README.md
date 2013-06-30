# nzbspider

Takes input in the form of either a list of release names or a 
configuration file (matching database entries), and then searches for
and downloads the corresponding NZBs.

## Sources

Currently uses nzbindex.nl and binsearch.info. Shouldn't be hard to
extend. Contributions welcome.

## Installing

You'll need to `pip install oursql requests` (this will require having 
the MySQL development libraries installed). Other than that, just run 
main.py.

## Notes

The script will assume that all releasenames in your database are safe
as a filename. No sanitation or conversion of the filenames will take
place.

## License

Licensed under the WTFPL or, if you take issue with that for some
reason, the CC0. Attribution (to Sven Slootweg) appreciated, not 
required.

## Donating

If you like this, you can donate 
[here](http://cryto.net/~joepie91/donate.html).
