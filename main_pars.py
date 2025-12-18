from ria import*
from lenta import*
from Kommersant import*


def main_func():
    parser1 = RiaNewsParser()
    parser2 = LentaNewsParser()
    parser3 = KommersantNewsParser()

    news1 = parser1.run_full_parsing()
    news2 = parser2.run_full_parsing_Lenta()
    news3 = parser3.run_full_parsing()


