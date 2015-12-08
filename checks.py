__author__ = 'carminecalicchio'

import internal_func

internal_func.setup_logging()

internal_func.logger = internal_func.logging.getLogger()

internal_func.filesystem_space()
internal_func.check_service()
internal_func.check_db()