import logging
import auto_deploy.process as process
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logger.debug('from demo')

with open('config.json', 'r') as f:
    config = json.load(f)
logger.debug(config)

ad = process.AutoDeploy(config)
