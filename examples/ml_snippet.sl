import std::ml

func main() {
    weights := [0.2, 0.8]
    features := [10, 3]
    pred := ml.predict_linear(weights, features, 1)
    print("prediction ${pred}")
}
