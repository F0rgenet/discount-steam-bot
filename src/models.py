class Game:
    def __init__(self, name: str, original_price: int | None, current_price: int | None, discount: int | None, url: str):
        self.name = name
        self.original_price = original_price
        self.current_price = current_price
        self.discount = discount
        self.url = url

    def __repr__(self):
        return f"Game(name={self.name}, price=({self.current_price}/{self.original_price}), discount={self.discount}, url={self.url})"