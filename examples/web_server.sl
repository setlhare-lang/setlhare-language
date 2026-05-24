import net::http

func app(req) {
    return http.Response("Hello from Setlhare at ${req.path}")
}

func main() {
    http.serve("127.0.0.1", 8080, app)
}
