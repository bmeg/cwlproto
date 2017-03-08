
package cwlproto

import (
  "fmt"
  proto "github.com/golang/protobuf/proto"
  "gopkg.in/yaml.v2"
  "io/ioutil"
)


func LoadCWL(path string, resolve bool) (proto.Message, error) {
  source, err := ioutil.ReadFile(path)
  if err != nil {
    return &GraphRecord{}, fmt.Errorf("Unable to parse file: %s", err)
  }
  doc := make(map[interface{}]interface{})
  err = yaml.Unmarshal(source, &doc)
  
  return &GraphRecord{}, nil
}
