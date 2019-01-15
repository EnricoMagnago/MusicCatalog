import os


class DbConfig():
    """SqlAlchemy-DB configuration"""

    def __init__(self):
        self.log = False

        config_file_dir = os.path.dirname(os.path.realpath(__file__))

        self.base_dir = os.path.join(config_file_dir, '..', '..', '..')
        self.base_dir = os.path.abspath(self.base_dir)
        assert os.path.isdir(self.base_dir), \
            f"Not a directory: {self.base_dir}"

        self.resources_dir = os.path.join(self.base_dir, 'resources')
        assert os.path.isdir(self.resources_dir), \
            f"Not a directory: {self.resources_dir}"

        db_file = os.path.join(self.resources_dir, 'db')
        assert os.path.isdir(db_file), \
            f"Not a directory: {db_file}"
        db_file = os.path.join(db_file, 'gbc.db')
        self.connection_uri = f"sqlite:///{db_file}"

        self.music_sheets_base_path = os.path.join(self.resources_dir,
                                                   'music_sheets')
        assert os.path.isdir(self.music_sheets_base_path), \
            f"Not a directory: {self.music_sheets_base_path}"


DB_CONFIG = DbConfig()
