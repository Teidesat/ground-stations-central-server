# config/routers.py
"""Database router for directing telemetry and control models to TimescaleDB."""

class TimescaleRouter:
    """Route models belonging to telemetry/control app to TimescaleDB,
    while keeping all other models in the default PostgreSQL database.
    """

    route_app_labels = {'control'}

    def db_for_read(self, model, **hints):
        """Direct read operations for control models to TimescaleDB."""
        if model._meta.app_label in self.route_app_labels:
            return 'timescale'
        return 'default'

    def db_for_write(self, model, **hints):
        """Direct write operations for control models to TimescaleDB."""
        if model._meta.app_label in self.route_app_labels:
            return 'timescale'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if both models are in the same database."""
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return obj1._meta.app_label == obj2._meta.app_label
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure control models only migrate on TimescaleDB,
        and general models only migrate on the default database.
        """
        if app_label in self.route_app_labels:
            return db == 'timescale'
        return db == 'default'