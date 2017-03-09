
package cwlproto

import (
  "fmt"
  "log"
  proto "github.com/golang/protobuf/proto"
  "github.com/golang/protobuf/jsonpb"
  "gopkg.in/yaml.v2"
  "io/ioutil"
  "encoding/json"
)

type JSONDict map[interface{}]interface{}

func LoadCWL(path string, resolve bool) (proto.Message, error) {
  source, err := ioutil.ReadFile(path)
  if err != nil {
    return &GraphRecord{}, fmt.Errorf("Unable to parse file: %s", err)
  }
  doc := make(map[interface{}]interface{})
  err = yaml.Unmarshal(source, &doc)
  if err != nil {
    return &GraphRecord{}, fmt.Errorf("Unable to parse file: %s", err)
  }

  doc = prep_doc(doc)

  if doc["class"] == "CommandLineTool" {
    log.Printf("Found CommandLineTool")
    b, err := json.Marshal(mapNormalize(doc))
    if err != nil {
      return &GraphRecord{}, fmt.Errorf("Unable to parse file: %s", err)
    }
    log.Printf("JSON: %s", b)
    out := CommandLineTool{}
    err = jsonpb.UnmarshalString(string(b), &out)
    return &out, err
  }

  return &GraphRecord{}, nil
}


func mapNormalize(v interface{}) interface{} {
	if base, ok := v.(map[interface{}]interface{}); ok {
		out := map[string]interface{}{}
		for k, v := range base {
			out[k.(string)] = mapNormalize(v)
		}
		return out
	} else if base, ok := v.(JSONDict); ok {
		out := map[string]interface{}{}
		for k, v := range base {
			out[k.(string)] = mapNormalize(v)
		}
		return out

	} else if base, ok := v.([]interface{}); ok {
		out := make([]interface{}, len(base))
		for i, v := range base {
			out[i] = mapNormalize(v)
		}
		return out
	}
	return v
}


func prep_doc(doc JSONDict) JSONDict {

  if doc["class"] == "CommandLineTool" {
      doc = prep_CommandLineTool(doc)
  }

  return doc
}

func prep_CommandLineTool(doc JSONDict) JSONDict {

  return doc
}
