from abc import ABC, abstractmethod

class ui(ABC):
    @abstractmethod
    def run(self):
        raise NotImplementedError

class gui(Ui):
    def __init__(self):
        pass

    def run(self):
        pass

class terminal(Ui):
    def __init__(self):
        pass

    def run(self):
        pass