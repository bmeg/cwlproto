
package main

import (
  "os"
  "fmt"
  "github.com/bmeg/cwlproto"
)


func main() {
  file := os.Args[1]
  pb, err := cwlproto.LoadCWL(file, true)
  if err != nil {
    fmt.Fprintf(os.Stderr, "Error parsing file: %s\n", err)
    os.Exit(1)
  }
  fmt.Printf("%s\n", pb)
}
