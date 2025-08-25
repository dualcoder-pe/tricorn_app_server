import sys

from batch.trifin.backtesting.rebalance import run_backtesting
from lib.exception_utils import print_exception_detail
from lib.logger import get_logger

logger = get_logger()

if __name__ == "__main__":
    try:
        run_backtesting()
        # run_backtesting_with_cut_loss()
    except Exception as e:
        logger.error("[오류] 백테스트 실행 실패:", e)
        print_exception_detail(e)
        sys.exit(1)
