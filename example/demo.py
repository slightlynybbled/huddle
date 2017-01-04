import logging
import json

from auto_deploy.manage import ApplicationManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

with open('demo_config.json', 'r') as f:
    config = json.load(f)
logger.debug('config: '.format(config))

ad = ApplicationManager(config)
