To avoid overloading the production server, we made a backup of its database.
You first need to import the database before running the parsing scripts.

## How to import the InfluxDB backup folder:

```
sudo influxd restore -metadir <influxdb_meta_dir> <backup_dir>
sudo influxd restore -database <influxdb_data_dir> <backup_dir>
```

#### Exemple

```
sudo influxd restore -metadir /var/lib/influxdb/meta/ 17.03.13-00/
sudo influxd restore -database realms -datadir /var/lib/influxdb/data 17.03.13-00
```
