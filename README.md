# artvee-scraper

 **artvee-scraper** is an easy to use command line utility for fetching public domain artwork from https://www.artvee.com.

- [Artvee Web-scraper](#artvee-scraper)
  - [Installation](#installation)
  - [Synopsis](#synopsis)
  - [Examples](#examples)
  - [Available Commands](#available-commands)

## Installation

Using PyPI
```console
$ python -m pip install artvee-scraper
```
Python 3.8+ is officially supported.

## Synopsis
```console
artvee-scraper <command> [optional arguments] [positional arguments]
```

## Examples
View help
```console
$ artvee-scraper -h
usage: artvee-scraper [-h] {log-json,file-json,file-multi} ...

Scrape artwork from https://www.artvee.com

positional arguments:
  {log-json,file-json,file-multi}
    log-json            Artwork is output to the log as a JSON object
    file-json           Artwork is represented as a JSON object and written to a file
    file-multi          Artwork image and metadata are written as separate files

optional arguments:
  -h, --help            show this help message and exit
```

View help for the *file-json* command
```console
$ artvee-scraper file-json -h
usage: artvee-scraper file-json [-h] [-t [1-16]] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                    [-c {abstract,figurative,landscape,religion,mythology,posters,animals,illustration,still-life,botanical,drawings,asian-art}]
                    [--log-dir LOG_DIR] [--log-max-size [1-10240]] [--log-max-backups [0-100]]
                    [--space-level [2-6]] [--sort-keys] [--overwrite-existing]
                    dir_path

positional arguments:
  dir_path              JSON file output directory

optional arguments:
  -h, --help            show this help message and exit
  -t [1-16], --worker-threads [1-16]
                        Number of worker threads (1-16)
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the application log level
  -c {abstract,figurative,landscape,religion,mythology,posters,animals,illustration,still-life,botanical,drawings,asian-art}, --category {abstract,figurative,landscape,religion,mythology,posters,animals,illustration,still-life,botanical,drawings,asian-art}
                        Category of artwork to scrape
  --space-level [2-6]   Enable pretty-printing; number of spaces to indent (2-6)
  --sort-keys           Sort JSON keys in alphabetical order
  --overwrite-existing  Overwrite existing files

optional log file arguments:
  --log-dir LOG_DIR     Log file output directory
  --log-max-size [1-10240]
                        Maximum log file size in MB (1-10,240)
  --log-max-backups [0-100]
                        Maximum number of log files to keep (0-100)
```

Download artwork from *artvee.com* and save each as individal files (JSON format) in the directory *~/artvee/downloads*
```console
$ artvee-scraper file-json ~/artvee/downloads
```

## Available Commands
- [log-json](#log-json)
- [file-json](#file-json)
- [file-multi](#file-multi)

## log-json
Download artwork and output each to the log as a JSON objects.
Note: This command is intended for development test usage; typically it is not desirable to dump the data to the log.
```console
$ artvee-scraper log-json [optional arguments]
```

###### Optional arguments
> `-h` | `--help` (boolean)
>> Display help message.

> `-t` | `--worker-threads` (integer)
>> The number of worker threads used for processing. Range of values is [1-16]. The default value is *3*.

> `-l` | `--log-level` (string)
>> Application log level. One of: **DEBUG, INFO, WARNING, ERROR, CRITICAL**. The default value is *INFO*.

>`-c` | `--category` (string)
>> Category of artwork to fetch. One of: **abstract, figurative, landscape, religion, mythology, posters, animals, illustration, still-life,  botanical, drawings, asian-art**. May be repeatedly used to specify multiple categories (*-c animals, -c drawings*). The default value is *ALL*   categories.

###### Optional log file arguments
> `--log-dir` (string)
>> Path to existing directory used to store *artvee_scraper.log* log files. Disabled by default.

> `--log-max-size` (integer)
>> Maximum size in MB the log file should reach before triggering a rollover. Only applies if *--log-dir* has been specified. Range of values is [1-10240]. The default value is *1024*MB (1GB).

> `--log-max-backups` (integer)
>> Maximum number of log file archives to keep. Only applies if *--log-dir* has been specified. The actively written file is *artvee_scraper.log*. Backup files will have an incrementing numerical suffix; *artvee_scraper.log.1 ... artvee_scraper.log.N*. If this value is zero, rollovers will be disabled. Range of values is [0-100]. The default value is *10*.

###### Optional writer arguments
> `--space-level` (integer)
>> Pretty print JSON; number of spaces to indent. Range of values is [2-6]. Disabled by default.

> `--sort-keys` (boolean)
>> Sort JSON keys in alphabetical order. Disabled by default.

> `--include-image` (boolean)
>> Image will be included in output. Excessive output warning! Disabled by default.


###### Basic Example
```console
$ artvee-scraper log-json
```
###### Output:
```console
...
2038-01-19 03:14:07.988 DEBUG [ThreadPoolExecutor-0_0] scraper._image_link_from(120) | Retrieving image download link from URL https://artvee.com/dl/study-for-old-canal-red-green/
2038-01-19 03:14:07.989 DEBUG [ThreadPoolExecutor-0_0] connectionpool._new_conn(1001) | Starting new HTTPS connection (1): artvee.com:443
2038-01-19 03:14:07.999 INFO [ThreadPoolExecutor-0_0] log_writer.write(44) | {"url": "https://artvee.com/dl/study-for-old-canal-red-green/", "title": "Study for Old Canal (Red & Green)", "category": "Abstract", "artist": "Oscar Bluemner", "date": "1916", "origin": "American, 1867-1938"}
...
```

###### Advanced Example
```console
$ artvee-scraper log-json --worker-threads 2 --log-level DEBUG --category abstract --log-dir /var/log/artvee --log-max-size 2048 --log-max-backups 10 --space-level 2 --sort-keys --include-image
```
###### Output:
```console
$ cat /var/log/artvee/artvee_scraper.log
...
2038-01-19 03:14:07.988 DEBUG [ThreadPoolExecutor-0_0] scraper._image_link_from(120) | Retrieving image download link from URL https://artvee.com/dl/study-for-old-canal-red-green/
2038-01-19 03:14:07.989 DEBUG [ThreadPoolExecutor-0_0] connectionpool._new_conn(1001) | Starting new HTTPS connection (1): artvee.com:443
2038-01-19 03:14:07.999 INFO [ThreadPoolExecutor-0_0] log_writer.write(44) | {
  "artist": "Oscar Bluemner",
  "category": "Abstract",
  "date": "1916",
  "image": "/9j/4AAQSkZJRgABA ... o4xSSSVkumh//9k="
  "origin": "American, 1867-1938",
  "title": "Study for Old Canal (Red & Green)",
  "url": "https://artvee.com/dl/study-for-old-canal-red-green/"
}
...
```

## file-json
Download artwork and write each to the filesystem. Each artwork is stored as a JSON object.
```console
$ artvee-scraper file-json [optional arguments] <dir_path>
```

###### Positional arguments
> `dir_path` (string) Position *0*.
>> Path to existing directory used to store output files.

###### Optional arguments
> `-h` | `--help` (boolean)
>> Display help message.

> `-t` | `--worker-threads` (integer)
>> The number of worker threads used for processing. Range of values is [1-16]. The default value is *3*.

> `-l` | `--log-level` (string)
>> Application log level. One of: **DEBUG, INFO, WARNING, ERROR, CRITICAL**. The default value is *INFO*.

>`-c` | `--category` (string)
>> Category of artwork to fetch. One of: **abstract, figurative, landscape, religion, mythology, posters, animals, illustration, still-life,  botanical, drawings, asian-art**. May be repeatedly used to specify multiple categories (*-c animals, -c drawings*). The default value is *ALL*   categories.

###### Optional log file arguments
> `--log-dir` (string)
>> Path to existing directory used to store *artvee_scraper.log* log files. Disabled by default.

> `--log-max-size` (integer)
>> Maximum size in MB the log file should reach before triggering a rollover. Only enabled if *--log-dir* has been specified. Range of values is [1-10240]. The default value is *1024*MB (1GB).

> `--log-max-backups` (integer)
>> Maximum number of log file archives to keep. Only enabled if *--log-dir* has been specified. The actively written file is *artvee_scraper.log*. Backup files will have an incrementing numerical suffix; *artvee_scraper.log.1 ... artvee_scraper.log.N*. If this value is zero, rollovers will be disabled. Range of values is [0-100]. The default value is *10*.

###### Optional writer arguments
> `--space-level` (integer)
>> Pretty print JSON; number of spaces to indent. Range of values is [2-6]. Disabled by default.

> `--sort-keys` (boolean)
>> Sort JSON keys in alphabetical order. Disabled by default.

> `--overwrite-existing` (boolean)
>> Allow existing duplicate files to be overwritten. Disabled by default.

###### Basic Example
```console
$ artvee-scraper file-json ~/artvee/downloads
```
###### Output:
```console
$ cat ~/artvee/downloads/peter-nicolai-arbo-the-valkyrie.json
{"url": "https://artvee.com/dl/the-valkyrie-2/", "title": "The Valkyrie", "category": "Mythology", "artist": "Peter Nicolai Arbo", "date": "1869", "origin": "Norwegian, 1831–1892", "image": "/9j/4AAQSkZJRgABA ... o4xSSSVkumh//9k="}
```

###### Advanced Example
```console
$ artvee-scraper file-json --worker-threads 1 --log-level INFO --category mythology --log-dir /var/log/artvee --log-max-size 512 --log-max-backups 10 --space-level 4 --sort-keys --overwrite-existing ~/artvee/downloads
```
###### Output:
```console
$ cat ~/artvee/downloads/peter-nicolai-arbo-the-valkyrie.json
{
    "artist": "Peter Nicolai Arbo",
    "category": "Mythology",
    "date": "1869",
    "image": "/9j/4AAQSkZJRgABA ... o4xSSSVkumh//9k="
    "origin": "Norwegian, 1831–1892",
    "title": "The Valkyrie",
    "url": "https://artvee.com/dl/the-valkyrie-2/"
}
```

## file-multi
Download artwork and write each to the filesystem. Each artwork is stored as two files: metadata (JSON) & image (JPG).
```console
$ artvee-scraper file-multi [optional arguments] <metadata_dir_path> <image_dir_path>
```

###### Positional arguments
> `metadata_dir_path` (string) Position *0*.
>> Path to existing directory used to store output metadata files.

> `image_dir_path` (string) Position *1*.
>> Path to existing directory used to store output image files.

###### Optional arguments
> `-h` | `--help` (boolean)
>> Display help message.

> `-t` | `--worker-threads` (integer)
>> The number of worker threads used for processing. Range of values is [1-16]. The default value is *3*.

> `-l` | `--log-level` (string)
>> Application log level. One of: **DEBUG, INFO, WARNING, ERROR, CRITICAL**. The default value is *INFO*.

> `-c` | `--category` (string)
>> Category of artwork to fetch. One of: **abstract, figurative, landscape, religion, mythology, posters, animals, illustration, still-life,  botanical, drawings, asian-art**. May be repeatedly used to specify multiple categories (*-c animals -c drawings*). The default value is *ALL*   categories.

###### Optional log file arguments
> `--log-dir` (string)
>> Path to existing directory used to store *artvee_scraper.log* log files. Disabled by default.

> `--log-max-size` (integer)
>> Maximum size in MB the log file should reach before triggering a rollover. Only enabled if *--log-dir* has been specified. Range of values is [1-10240]. The default value is *1024*MB (1GB).

> `--log-max-backups` (integer)
>> Maximum number of log file archives to keep. Only enabled if *--log-dir* has been specified. The actively written file is *artvee_scraper.log*. Backup files will have an incrementing numerical suffix; *artvee_scraper.log.1 ... artvee_scraper.log.N*. If this value is zero, rollovers will be disabled. Range of values is [0-100]. The default value is *10*.

###### Optional writer arguments
> `--space-level` (integer)
>> Pretty print JSON; number of spaces to indent. Range of values is [2-6]. Disabled by default.

> `--sort-keys` (boolean)
>> Sort JSON keys in alphabetical order. Disabled by default.

> `--overwrite-existing` (boolean)
>> Allow existing duplicate files to be overwritten. Disabled by default.

###### Basic Example
```console
$ artvee-scraper file-multi ~/artvee/downloads/metadata ~/artvee/downloads/images
```
###### Output:
```console
$ cat ~/artvee/downloads/metadata/peter-nicolai-arbo-the-valkyrie.json
{"url": "https://artvee.com/dl/the-valkyrie-2/", "title": "The Valkyrie", "category": "Mythology", "artist": "Peter Nicolai Arbo", "date": "1869", "origin": "Norwegian, 1831–1892"}

$ cat ~/artvee/downloads/images/peter-nicolai-arbo-the-valkyrie.jpg
<FF><D8><FF><E0>^@^PJFIF^@^A^A^A^A,^A,^@^@<FF><E1><D5>$Exif^@^@II*^@^
...
^<X-nA2_vއ%6gS`QErVOOqk;R,u{w9~onDbsEWQ㿟xyr
```

###### Advanced Example
```console
$ artvee-scraper file-multi --worker-threads 1 --log-level INFO --category mythology --log-dir /var/log/artvee --log-max-size 512 --log-max-backups 10 --space-level 2 --sort-keys --overwrite-existing ~/artvee/downloads/metadata ~/artvee/downloads/images
```
###### Output:
```console
$ cat ~/artvee/downloads/metadata/peter-nicolai-arbo-the-valkyrie.json
{
  "artist": "Peter Nicolai Arbo",
  "category": "Mythology",
  "date": "1869",
  "origin": "Norwegian, 1831–1892",
  "title": "The Valkyrie",
  "url": "https://artvee.com/dl/the-valkyrie-2/"
}
$ cat ~/artvee/downloads/images/peter-nicolai-arbo-the-valkyrie.jpg
<FF><D8><FF><E0>^@^PJFIF^@^A^A^A^A,^A,^@^@<FF><E1><D5>$Exif^@^@II*^@^
...
^<X-nA2_vއ%6gS`QErVOOqk;R,u{w9~onDbsEWQ㿟xyr
```