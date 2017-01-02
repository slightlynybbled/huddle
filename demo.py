import logging
import auto_deploy.process as process

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logger.debug('from demo')

ad = process.AutoDeploy('config.json')
