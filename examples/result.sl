func safe_div(a, b) {
    if b == 0 {
        return Err("division by zero")
    }
    return Ok(a / b)
}

func main() {
    value := safe_div(10, 2)?
    print("value ${value}")
}
