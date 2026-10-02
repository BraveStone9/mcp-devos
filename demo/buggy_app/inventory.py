def calculate_average_price(items):
    total = sum(item["price"] for item in items)
    return total / len(items)


def apply_discount(prices, discount_index):
    return prices[discount_index] * 0.9


def main():
    items = [
        {"name": "Widget", "price": 10},
        {"name": "Gadget", "price": 20},
    ]
    avg = calculate_average_price(items)
    print(f"Average price: {avg}")

    prices = [10, 20]
    discounted = apply_discount(prices, 2)
    print(f"Discounted price: {discounted}")


if __name__ == "__main__":
    main()
