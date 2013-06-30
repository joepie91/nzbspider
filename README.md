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

## Usage

You can use nzbspider with either a release list or a configuration 
file.

### Release list

This is a text file, specified with the `--list` parameter, that
contains a newline-delimited list of release names to search for. You
will need to use the `--target` parameter to specify what directory to
download the NZBs to.

### Configuration file

This is a text file using a specific configuration syntax to select
specific releases from a pre-filled MySQl database, to search for. Use
the `--config` parameter to specify the path of the configuration file
you wish to use.

To use this mode, you will need to copy config.json.example to 
config.json and change the database details to match yours. A (basic) 
database schema is included. Only results that are at least 24 hours old
will be matched, regardless of your configuration.

The configuration file format is as follows:

* Newline-delimited, a new predicate on every line.
* Three whitespace-delimited fields: release name, section, and target 
  directory.
* Enter `-` for any or both of the first two fields to match regardless
  of the release name or section (depending on which you fill in as `-`).
* The `%` character is used to denote a multi-character wildcard
  anywhere in the first two fields.
* The first two fields are enclosed in wildcard characters by default.
* The target directory does not have to exist; it will be created if it
  doesn't.
* You must enclose a field value in `"` quotes if it contains a space.
  
An example configuration file (the real configuration format doesn't
allow comments, so don't copy this verbatim!):

	- MP3 ./mp3s             # Will select everything in section 'MP3'
	- - ./everything         # Will select absolutely everything
	IMMERSE - ./immerse      # Will select everything labeled 'IMMERSE'
	Mad.Men%720p - ./madmen  # Will select every 720p episode of Mad Men
	
Note that these searches are run against your own database, not directly
against the NZB indexing sites! You'll still need a list of valid 
release names pre-filled in your database.

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
