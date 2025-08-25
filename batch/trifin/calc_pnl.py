from src.config.db import get_db
from src.repository.models.order_table import Order, UnitEnum
import pandas as pd


def run():
    """
    order 테이블의 모든 주문을 시간순(오름차순)으로 불러와 DataFrame으로 반환합니다.
    """
    with get_db() as session:
        orders = session.query(Order).order_by(Order.date.asc()).all()
        df_orders = pd.DataFrame(
            [
                {c.name: getattr(row, c.name) for c in Order.__table__.columns}
                for row in orders
            ]
        )
        print("[INFO] 시간순 주문 내역:")
        print(df_orders)

        # Price 테이블에서 symbol='KRX=X' 환율 정보를 날짜별로 미리 조회
        from src.repository.models.price_table import Price
        price_rows = session.query(Price).filter(Price.symbol == 'KRW=X').all()
        # 환율 dict: {yyyymmdd: 환율}
        fx_map = {}
        for p in price_rows:
            # timestamp(datetime) → yyyymmdd 문자열로 변환
            if hasattr(p.timestamp, 'strftime'):
                date_str = p.timestamp.strftime('%Y-%m-%d')
            else:
                # 문자열/타입이 이미 yyyymmdd면 그대로 사용
                date_str = str(p.timestamp)
            fx_map[date_str] = p.close

        # 현금 흐름 및 전체 입금액 계산
        cash = 0.0
        total_deposit = 0.0
        for idx, row in df_orders.iterrows():
            # 환율 결정: USD면 해당 날짜의 환율, 아니면 1
            if row["unit"] == UnitEnum.USD:
                fx = fx_map.get(str(row["date"]), None)
                if fx is None:
                    print(f"[WARN] 환율 없음: {row['date']} → 1로 처리")
                    fx = 1.0
            else:
                fx = 1.0
            
            if row["type"].lower() == "buy":
                amount = row["size"] * row["price"] * fx
                cash -= amount
                # 현금 부족 시 입금 처리
                if cash < 0:
                    deposit = -cash
                    total_deposit += deposit
                    print(
                        f"[{row['date']}] 현금 부족 ({row['symbol']}): {deposit:.2f} 입금 (누적 입금: {total_deposit:.2f})"
                    )
                    cash = 0.0
            elif row["type"].lower() == "sell":
                amount = row["size"] * row["price"] * fx
                cash += amount
                print(f"[{row['date']}] 매도: +{amount:.2f} (현금: {cash:.2f})")
        print(f"\n[RESULT] 전체 입금액: {total_deposit:.2f}")
        return total_deposit


if __name__ == "__main__":
    run()
