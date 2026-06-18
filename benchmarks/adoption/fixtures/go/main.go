package main

import "fmt"

func Greet(name string) string {
	return "gadget:" + name
}

func main() {
	fmt.Println(Greet("world"))
}
