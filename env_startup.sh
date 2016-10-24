# Author(s): James Murphy

# script to start database service and install .sql file

sudo service postgresql start
echo "\i azure-leaf.sql" | psql