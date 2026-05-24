func main() {
    mut total = 0
    for n in range(1, 6) {
        total = total + n
    }
    if total > 10 {
        print("total is ${total}")
    } else {
        print("small")
    }
}
