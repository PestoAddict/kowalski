from ConfigMerger import ConfigMerger
from config.config import Settings

config = ConfigMerger()
settings: Settings = config.get_config("config")
