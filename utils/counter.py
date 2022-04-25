class Counter:
    value = 0

    @staticmethod
    def step() -> int:
        Counter.value += 1
        return Counter.value

