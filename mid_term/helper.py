def is_valid_isbn(isbn):
    isbn = isbn.replace("-", "").replace(" ", "").strip()

    def is_valid_isbn10(isbn):
        if len(isbn) != 10:
            return False

        total = 0
        for i in range(10):
            if isbn[i] == 'X' and i == 9:
                total += 10
            elif isbn[i].isdigit():
                total += int(isbn[i]) * (i + 1)
            else:
                return False

        return total % 11 == 0

    def is_valid_isbn13(isbn):
        if len(isbn) != 13 or not isbn.isdigit():
            return False

        total = 0
        for i in range(13):
            if i % 2 == 0:
                total += int(isbn[i])
            else:
                total += int(isbn[i]) * 3

        return total % 10 == 0

    if len(isbn) == 10:
        return is_valid_isbn10(isbn)
    elif len(isbn) == 13:
        return is_valid_isbn13(isbn)
    else:
        return False