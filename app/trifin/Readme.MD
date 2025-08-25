
# Backend

- Requirement
  - 매월 특정 금액 입금하면 실시간으로 수익률 확인
    - 유저 (`User`)
      - ID
      - 이름 (`name`): str
    - 계좌 (`Account`)
      - ID
      - 소유자 (`user_id`): str
      - 계좌 이름 (`name`): str
      - 잔고 (`balance`): float
    - 주문 (`Order`)
      - ID
      - 타입 (`type`): enum(buy or sell)
      - 종목 (`symbol`): str
      - 계좌 (`account_id`): str
      - 주문일 (`date`): datetime
      - 수량 (`size`): float
      - 단가 (`price`): float
    - 수익률 (`Profit`)
      - ID
      - 유저 (`user_id`): str
      - 계좌 (`account_id`): str
      - 수익률 (`profit`): float