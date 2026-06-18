package main

import "testing"

func TestGreet(t *testing.T) {
	if Greet("x") != "gadget:x" {
		t.Fatal("unexpected greeting")
	}
}
