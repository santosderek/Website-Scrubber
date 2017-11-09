# Website-Scrubber
A script which incorporates multi-threading to scrub through a web-directory for downloads.

***

### How to install:

*** Repository developed in Python 3.6.x ***

*Copy repository from github:*

    git clone https://github.com/santosderek/Website-Scrubber

*Move into repository*

    cd Website-Scrubber

*Install Python Package*

    python3 setup.py install

*Congrats, it's installed! Now you can proceed bellow*

***

### How to use:
#### Following commands can be used:
***Base command:***

    ws [options] URLS



***Help page***

*View the help page*

    ws --help

***Base Command***

*Multiple urls can be used at once.*

    ws URLS

***Scrub Through All Sub-Directories***

*Sets RECURSION_LEVEL to 9^99*

    ws -r URLS | OR | ws --recursion URLS

***Scrub Through A Limited Number Of Sub-Directories***

*RECURSION_LEVEL is the number of recursion attempts that are allowed.*

    ws --level [RECURSION_LEVEL] URLS | OR | ws -l [RECURSION_LEVEL] URLS

*If set to 1: Script will go down one sub-directory level.*

*If set to 2: Script will go down two sub-directory levels.*

*If set to 3: Script will go down two sub-directory levels.*

*etc...*


***Number Of Threads To Use***

*By default 3 threads will be used.*

    ws --threads [NUMBER_OF_THREADS] URLS | OR | ws -t [NUMBER_OF_THREADS] URLS

***Folder Download Path To Use***

    ws --folder [path/to/download/directory] URLS | OR | ws -f [path/to/download/directory] URLS
