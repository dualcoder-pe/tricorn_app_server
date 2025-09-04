import judical
import tax
import labor
import lawyer
import realtor
import patent
import datetime


def run():
    today = datetime.date.today().strftime("%Y-%m-%d")
    patent.run(today)
    judical.run(today)
    tax.run(today)
    labor.run(today)
    lawyer.run(today)
    realtor.run(today)



if __name__ == "__main__":
    run()
