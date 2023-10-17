def count_rectangles(n, m):
    # Calculate the number of rectangles using combinations of horizontal and vertical lines
    total_rectangles = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Calculate the number of rectangles that can be formed using i horizontal lines and j vertical lines
            rectangles_with_i_lines = (n - i + 1) * (m - j + 1)
            total_rectangles += rectangles_with_i_lines

    return total_rectangles


# Example usage
n = 3  # Number of rows
m = 4  # Number of columns
result = count_rectangles(n, m)
print(f"Number of rectangles in a {n}x{m} grid: {result}")
