import logging
from queue import Empty, Full, Queue
from threading import Thread
from time import monotonic, time

from ProjectConfig.Project import getProject
from externalParameter.persistence import persistenceProviders, persistenceDict

try:
    from influxdb import InfluxDBClient
    from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
    from requests.exceptions import RequestException

    class TelemetryWriter:
        def __init__(self, host, database):
            self.client = InfluxDBClient(
                host=host, port=8086, database=database, timeout=2, retries=1
            )
            self.points = Queue(maxsize=512)
            Thread(target=self.run, name="InfluxDB telemetry", daemon=True).start()

        def record(self, point):
            try:
                self.points.put_nowait(point)
            except Full:
                # A database outage should never block acquisition.
                pass

        def run(self):
            next_warning = 0
            while True:
                batch = [self.points.get()]
                try:
                    for _ in range(127):
                        batch.append(self.points.get_nowait())
                except Empty:
                    pass

                try:
                    self.client.write_points(batch)
                except (RequestException, InfluxDBClientError, InfluxDBServerError, ValueError) as exc:
                    now = monotonic()
                    if now >= next_warning:
                        logging.getLogger(__name__).warning(
                            "InfluxDB telemetry write failed: %s", exc
                        )
                        next_warning = now + 30

    class TimeseriesPersist:
        store = None
        telemetry = None
        name = "Timeseries persist"

        def __init__(self):
            self.initialized = False
            self.active = True
            self.initDB()

        def __setstate__(self, state):
            self.__dict__.update(state)
            self.initialized = False

        def initDB(self):
            project = getProject()
            self.projectName = project.name
            databases = project.software.get("Timeseries Database", {})
            self.telemetryDatabase = databases.get("ioncontrol")
            default_database = next(
                (config for name, config in databases.items() if name != "ioncontrol"),
                None,
            )
            self.database = self.telemetryDatabase or default_database
            if default_database and TimeseriesPersist.store is None:
                TimeseriesPersist.store = InfluxDBClient(
                    host=default_database.get("host"),
                    port=8086,
                    database=default_database.get("database"),
                )
            self.active = TimeseriesPersist.store is not None
            self.initialized = True
            return self.active

        def record(self, measurement, fields, timestamp=None, tags=None):
            if not self.database:
                return
            if TimeseriesPersist.telemetry is None:
                TimeseriesPersist.telemetry = TelemetryWriter(
                    self.database.get("host"), self.database.get("database")
                )
            TimeseriesPersist.telemetry.record({
                "measurement": measurement,
                "tags": dict(tags or {}, project=self.projectName),
                "fields": fields,
                "time": int(time() * 1_000_000_000) if timestamp is None else timestamp,
            })


        def persist(self, space, source, time, value, minval=None, maxval=None, unit=None):
            if not self.active:
                return
            if source:
                try:
                     TimeseriesPersist.store.write_points([{
                        "measurement": source,
                        "tags": {
                            "space": space,
                            "project": getProject().name,
                        },
                        "fields": {
                            "valuef": float(value) if value is not None else None,
                            "minvalf": float(minval) if minval is not None else None,
                            "maxvalf": float(maxval) if maxval is not None else None,
                            "unit": unit
                        },
                         "time": time if time > 1000000000000000000 else int(time * 1000000000)
                    }])
                except ConnectionError as e:
                    logging.getLogger(__name__).warning("Cannot persist to timeseries database {}".format(e))

        def rename(self, space, oldsourcename, newsourcename):
            pass

        def paramDef(self):
            return []

        def sourceDict(self):
            return {}

    persistenceProviders.append(TimeseriesPersist)
    persistenceDict[TimeseriesPersist.name] = TimeseriesPersist

except:
    pass