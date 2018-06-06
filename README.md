# pdbops

Script to automate the database import on mySql / MariaDB.

The script performs the following actions:
1. dump of the current database
2. drop of the current database
3. creation of the new database with the same name
4. import of the selected (new) dump

### Setup

- create a new config file `config.cng` from the example file.
- insert the database parameters

e.g.:

```shell
[client]
user = root
password = root
host = localhost
```

### Import a dump
- Create a folder `import` and insert here all the dump files you want to import.
    **NOTE:** The file must to be in the format `filename.sql`.
- Launch the script with:

  ```shell
  python dbops.py
  ```

  or (if you are in a unix system)
  ```shell
  ./dbops.py
  ```

  and follow the instruction on the screen.

