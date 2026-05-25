// Setlhare structs, enums, methods, and pattern matching

struct Point { x, y }

impl Point {
    func distance_sq() => self.x * self.x + self.y * self.y
}

enum Shape {
    Circle(r),
    Rect(w, h),
    Dot,
}

impl Shape {
    func area() {
        match self {
            case Shape::Circle(r) => 3 * r * r
            case Shape::Rect(w, h) => w * h
            case Shape::Dot => 0
        }
    }
}

func main() {
    p := Point { x: 3, y: 4 }
    print("origin distance^2 = ${p.distance_sq()}")

    shapes := [Shape::Circle(2), Shape::Rect(3, 5), Shape::Dot]
    for s in shapes {
        print("area = ${s.area()}")
    }
}
