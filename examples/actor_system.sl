func worker(name) {
    print("actor ${name} started")
}

func main() {
    task := spawn worker("oak")
    task.join()
}
