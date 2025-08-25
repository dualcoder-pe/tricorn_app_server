import pandas as pd

from src.config.db import get_db
from src.repository.models.account_table import Account


def read_csv(filepath: str = "./sample.csv") -> pd.DataFrame:
    """
    sample.csv 파일을 읽어 DataFrame으로 반환합니다.

    Args:
        filepath (str): CSV 파일 경로 (기본값: ./sample.csv)
    Returns:
        pd.DataFrame: CSV 데이터프레임
    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때 발생
        pd.errors.ParserError: CSV 파싱 오류
    """
    try:
        df = pd.read_csv(filepath)

        # date 컬럼을 datetime.date 타입으로 변환
        try:
            df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.date
        except Exception as e:
            print("[ERROR] date 컬럼 변환 실패:", e)
            raise e

        # 데이터 미리보기 출력 (디버깅용)
        print("[INFO] CSV 미리보기:\n", df.head())
    except FileNotFoundError as e:
        print(f"[ERROR] 파일을 찾을 수 없습니다: {filepath}")
        raise e
    except pd.errors.ParserError as e:
        print(f"[ERROR] CSV 파싱 오류: {filepath}")
        raise e

    df_account = insert_account(df["account"])
    insert_order(df, df_account)


def insert_account(series: pd.Series) -> pd.DataFrame:
    """
    unique_account 리스트를 Account 테이블에 저장하고, 전체 테이블을 DataFrame으로 반환합니다.
    Args:
        series (pd.Series): 계좌명 시리즈 (account 컬럼)
    """
    unique_account = series.unique()
    print("[INFO] 추출된 계좌명:", unique_account)

    with get_db() as session:
        try:
            # 이미 존재하는 계좌명은 중복 삽입 방지
            for name in unique_account:
                exists = session.query(Account).filter_by(name=name).first()
                if not exists:
                    # user_id, balance는 임시로 1, 0.0 사용 (실제 로직에 맞게 수정 필요)
                    if name.startswith("태규"):
                        user_id = 1
                    elif name.startswith("윤지"):
                        user_id = 2
                    else:
                        raise Exception(f"Unexpected Account Name {name}")
                    acc = Account(user_id=user_id, name=name, balance=0.0)
                    session.add(acc)
            session.commit()
            print("[INFO] Account 테이블 저장 완료")

            # Account 테이블 전체를 DataFrame으로 조회
            result = session.query(Account).all()
            df_accounts = pd.DataFrame(
                [
                    {c.name: getattr(row, c.name) for c in Account.__table__.columns}
                    for row in result
                ]
            )
            print("[INFO] Account 테이블 전체:")
            print(df_accounts)
            return df_accounts
        except Exception as e:
            session.rollback()
            print("[ERROR] Account 저장/조회 실패:", e)
            raise e


def insert_order(df, df_account):
    with get_db() as session:
        # df와 df_account를 계좌명(name) 기준으로 merge하여 account_id 컬럼 추가
        # df: 원본 데이터프레임, df_account: Account 테이블 전체(id, name 등)
        try:
            # account_id 추가를 위해 merge (left join)
            df_merged = pd.merge(
                df,
                df_account[["id", "name"]],
                how="left",
                left_on="account",
                right_on="name",
            )
            df_merged = df_merged.rename(columns={"id": "account_id"})

            # 2. symbol이 _USD로 끝나면 unit=USD, 아니면 KRW
            df_merged["unit"] = df_merged["symbol"].apply(
                lambda x: "USD" if str(x).endswith("_USD") else "KRW"
            )

            # 3. symbol에서 _USD 접미어 제거
            df_merged["symbol"] = df_merged["symbol"].apply(
                lambda x: str(x)[:-4] if str(x).endswith("_USD") else x
            )

            df_merged["type"] = df_merged["type"].apply(
                lambda x: "Buy" if x == "매수" else "Sell"
            )

            df_merged["size"] = df_merged["size"].apply(
                lambda x: x * -1 if x < 0 else x
            )

            df_merged.drop(columns=["account", "name"], inplace=True)

            print("[INFO] 주문 데이터(account_id 추가):\n", df_merged.head())

            # Order 테이블에 저장
            from src.repository.models.order_table import Order
            order_objs = []
            for _, row in df_merged.iterrows():
                order = Order(
                    type=row["type"],
                    symbol=row["symbol"],
                    account_id=row["account_id"],
                    date=row["date"],
                    size=row["size"],
                    price=row["price"],
                    unit=row["unit"]
                )
                order_objs.append(order)
            session.add_all(order_objs)
            session.commit()
            print(f"[INFO] {len(order_objs)}건 Order 테이블 저장 완료")

            # Order 테이블 전체를 DataFrame으로 조회
            result = session.query(Order).all()
            df_orders = pd.DataFrame([
                {c.name: getattr(row, c.name) for c in Order.__table__.columns}
                for row in result
            ])
            print("[INFO] Order 테이블 전체:")
            print(df_orders)
            return df_orders
        except Exception as e:
            print("[ERROR] 주문-계좌 merge 실패:", e)
            raise e


if __name__ == "__main__":
    read_csv()
