#!/bin/bash

export GOPATH=`pwd`

go get github.com/golang/protobuf/protoc-gen-go/
export PATH=`pwd`/bin:$PATH
protoc --go_out=Mgoogle/protobuf/struct.proto=github.com/golang/protobuf/ptypes/struct:./ cwl.proto
