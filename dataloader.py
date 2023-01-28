from abc import ABC


class DataLoader:

    def __int__(self):
        A = 1

    def load_config(self):
        raise NotImplementedError

    def return_df(self):
        return 1


class PolygonData(DataLoader):

    def __int__(self):
        super(PolygonData, self).__int__()

    def load_config(self):
        return 1


class YFinanceData(DataLoader):

    def __int__(self):
        super(YFinanceData, self).__int__()

    def load_config(self):
        return 1
