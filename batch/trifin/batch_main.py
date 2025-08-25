import sys
from batch.trifin.information_collector import save_symbol_price
from batch.trifin.information_collector.save_index_price import save_index_price


def batch_main():
    start = "2005-01-01"
    save_symbol_price(start)
    save_index_price(start)
    return 0


if __name__ == "__main__":
    sys.exit(batch_main())
