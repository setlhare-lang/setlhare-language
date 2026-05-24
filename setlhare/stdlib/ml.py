def dot(a, b): return sum(x*y for x, y in zip(a, b))
def predict_linear(weights, features, bias=0): return dot(weights, features) + bias
def mse(predictions, targets): return sum((p-t)**2 for p, t in zip(predictions, targets)) / len(predictions)
