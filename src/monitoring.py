def get_sums(items):
    negative_values = 0
    positive_values = 0

    for item in items:
        if item < 0:
            negative_values += -item
        else:
            positive_values += item
    return positive_values, negative_values
