import std::embed

func main() {
    led := embed.pin(13, "out")
    embed.write(led, 1)
    print("pin value ${embed.read(led)}")
}
