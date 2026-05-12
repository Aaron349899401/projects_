import numpy as np

image_chunk = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
])

filter_kernel = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
])

activation_score = np.sum(image_chunk, * filter_kernel)

print(f"behold: {activation_score}")
