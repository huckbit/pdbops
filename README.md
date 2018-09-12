# pdbops

Script to automate the database import on mySql / MariaDB.

The script performs the following actions:
1. backup dump (current database) 
2. drop (current database)
3. new database creation (using the same name)
4. selected database (new) dump import

### Setup

- Clone the repository
- Install the package [PymySQL](https://github.com/PyMySQL/PyMySQL#installation).
- Create a new config file `config.cng` from the example file.
- Insert the database parameters

e.g.:

```shell
[client]
user = root
password = root
host = localhost
```

### Import a new dump
- In the folder `import` insert the dump files you want to import.
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

