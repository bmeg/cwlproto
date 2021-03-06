
import os
import yaml
import sys
import json
from copy import deepcopy
from google.protobuf.json_format import ParseDict, MessageToDict, ParseError
from .cwl_pb2 import CommandLineTool, ExpressionTool, Workflow, GraphRecord

def fields_dict2list(doc, *args, **kwargs):
    out = {}
    for k,v in doc.items():
        if k in args:
            if isinstance(v, dict):
                nv = []
                for ek, ev in v.items():
                    if isinstance(ev, basestring) or isinstance(ev, list):
                        i = {kwargs.get("id", "id") : ek, kwargs["field"]:ev}
                    else:
                        i = deepcopy(ev)
                        i[kwargs.get("id", "id")] = ek
                    nv.append(i)
                out[k] = nv
            else:
                out[k] = v
        else:
            out[k] = v
    return out

def fields_forcelist(doc, *args):
    out = {}
    for k,v in doc.items():
        if k in args:
            if not isinstance(v, list):
                out[k] = [v]
            else:
                out[k] = v
        else:
            out[k] = v
    return out

def prep_TypeRecord(doc):
    if isinstance(doc, basestring):
        if doc.endswith("[]"):
            return { "array" : {"items" : prep_TypeRecord(doc[:-2]) } }
        else:
            return {"name" : doc}
    if isinstance(doc, dict):
        out = None
        if doc['type'] == "array":
            out = { "array" : {"items" : prep_TypeRecord(doc['items']) } }
        if doc['type'] == "record":
            fields = []
            for i in doc['fields']:
                fields.append( { "name" : i['name'], "type" : prep_TypeRecord(i['type'])} )
            out = {"record" : { "name" : doc["name"], "fields" : fields } }
        if doc['type'] == "enum":
            out = {"enum" : {"name" : doc["name"], "symbols" : doc['symbols'] }}
        if out is not None:
            if 'inputBinding' in doc:
                out['inputBinding'] = doc['inputBinding']
            return out
    if isinstance(doc, list):
        t = []
        for i in doc:
            t.append(prep_TypeRecord(i))
        return {"oneof" : {"types" : t}}
    return doc

def prep_DataRecord(doc):
    if isinstance(doc, basestring):
        return {"string_value" : doc}
    if isinstance(doc, dict):
        return {"struct_value" : doc}
    if isinstance(doc, list):
        return {"list_value" : doc}
    if isinstance(doc, float):
        return {"float_value" : doc}
    if isinstance(doc, int):
        return {"int_value" : doc}
    return doc

def prep_InputRecordField(doc):
    #doc = fields_forcelist(doc, "doc")
    doc['type'] = prep_TypeRecord(doc['type'])
    if 'default' in doc:
        doc['default'] = prep_DataRecord(doc['default'])
    return doc

def prep_OutputRecordField(doc):
    #doc = fields_forcelist(doc, "doc", "outputSource")
    doc = fields_forcelist(doc, "outputSource")
    doc['type'] = prep_TypeRecord(doc['type'])
    if 'outputBinding' in doc:
        doc['outputBinding'] = prep_CommandOutputBinding(doc['outputBinding'])
    #if 'outputSource' in doc:
    #    doc['outputBinding'] = prep_CommandOutputBinding(doc['outputBinding'])

    return doc

def prep_CommandOutputBinding(doc):
    doc = fields_forcelist(doc, "glob")
    return doc

def prep_InputRecordField_list(doc):
    out = []
    for i in doc:
        out.append(prep_InputRecordField(i))
    return out

def prep_OutputRecordField_list(doc):
    out = []
    for i in doc:
        out.append(prep_OutputRecordField(i))
    return out

def prep_CommandLineBinding(doc):
    if isinstance(doc, basestring):
        return {"valueFrom" : doc}
    return doc

def prep_CommandLineBinding_list(doc):
    out = []
    for i in doc:
        out.append(prep_CommandLineBinding(i))
    return out

def prep_WorkflowStepOutput(doc):
    if isinstance(doc, basestring):
        return {"id" : doc}
    return doc

def prep_WorkflowStepOutput_list(doc):
    out = []
    for i in doc:
        out.append(prep_WorkflowStepOutput(i))
    return out

def prep_WorkflowStepInput(doc):
    #if isinstance(doc, basestring):
    #    return {"source" : [doc]}
    doc = fields_forcelist(doc, "source")
    if 'default' in doc:
        doc['default'] = prep_DataRecord(doc['default'])
    return doc

def prep_WorkflowStepInput_list(doc):
    out = []
    for i in doc:
        out.append(prep_WorkflowStepInput(i))
    return out

def prep_RunRecord(doc):
    if isinstance(doc, basestring):
        return {"path" : doc}
    if isinstance(doc, dict) and "class" in doc:
        e = prep_doc(doc)
        if e['class'] == "Workflow":
            return {"workflow" : e}
        if e['class'] == "ExpressionTool":
            return {"expression" : e}
        if e['class'] == "CommandLineTool":
            return {"commandline" : e}
    return doc

def prep_WorkflowStep(doc):
    doc = fields_forcelist(doc, "scatter")
    if "out" in doc:
        doc["out"] = prep_WorkflowStepOutput_list(doc["out"])
    if "run" in doc:
        doc["run"] = prep_RunRecord(doc["run"])
    if "in" in doc:
        doc = fields_dict2list(doc, "in", field="source")
        doc["in"] = prep_WorkflowStepInput_list(doc["in"])

    return doc

def prep_WorkflowStep_list(doc):
    out = []
    for i in doc:
        out.append(prep_WorkflowStep(i))
    return out


def prep_CommandLineTool(doc):
    doc = fields_dict2list(doc, "inputs", "outputs", field="type")
    doc = fields_dict2list(doc, "hints", "requirements", field="type", id="class")
    #doc = fields_forcelist(doc, "baseCommand", "doc")
    doc = fields_forcelist(doc, "baseCommand")
    if 'inputs' in doc:
        doc['inputs'] = prep_InputRecordField_list(doc['inputs'])
    if 'outputs' in doc:
        doc['outputs'] = prep_OutputRecordField_list(doc['outputs'])
    if 'arguments' in doc:
        doc['arguments'] = prep_CommandLineBinding_list(doc['arguments'])
    return doc


def prep_ExpressionTool(doc):
    doc = fields_dict2list(doc, "inputs", "outputs", "hints", "requirements", field="type")
    #doc = fields_forcelist(doc, "baseCommand", "doc")
    doc = fields_forcelist(doc, "baseCommand")
    if 'inputs' in doc:
        doc['inputs'] = prep_InputRecordField_list(doc['inputs'])
    if 'outputs' in doc:
        doc['outputs'] = prep_OutputRecordField_list(doc['outputs'])
    return doc

def prep_Workflow(doc):
    doc = fields_dict2list(doc, "inputs", "outputs", "hints", "requirements", "steps", field="type")
    if 'inputs' in doc:
        doc['inputs'] = prep_InputRecordField_list(doc['inputs'])
    if 'outputs' in doc:
        doc['outputs'] = prep_OutputRecordField_list(doc['outputs'])
    if 'steps' in doc:
        doc['steps'] = prep_WorkflowStep_list(doc['steps'])
    return doc

def resolve_Workflow(doc, doc_path, loaded_classes):
    if 'steps' in doc:
        for i in doc['steps']:
            if 'path' in i['run']:
                if i['run']['path'].startswith("#"):
                    found = None
                    for k in loaded_classes:
                        c = None
                        for v in ['commandline', 'expression', 'workflow']:
                            if v in k:
                                c = k[v]
                        if c is not None:
                            if c['id'] == i['run']['path'][1:]:
                                found = k
                    if found is not None:
                        i['run'] = found
                else:
                    new_path = os.path.join(os.path.dirname(doc_path), i['run']['path'] )
                    new_class = load_cwl(new_path, resolve=True)
                    new_doc = to_dict(new_class)
                    if new_doc['class'] == "CommandLineTool":
                        i['run'] = { "commandline" : new_doc }
                    if new_doc['class'] == "ExpressionTool":
                        i['run'] = { "expression" : new_doc }
                    if new_doc['class'] == "Workflow":
                        i['run'] = { "workflow" : new_doc }
    return doc

MUTATORS = {
    "CommandLineTool" : prep_CommandLineTool
}

def prep_doc(doc):
    if doc['class'] == "CommandLineTool":
        doc = prep_CommandLineTool(doc)
    if doc['class'] == "ExpressionTool":
        doc = prep_ExpressionTool(doc)
    if doc['class'] == "Workflow":
        doc = prep_Workflow(doc)
    #print json.dumps(doc, indent=4)
    return doc

def load_cwl(path, resolve=False):
    module = None
    if path.count("#") > 0:
        path, module = path.split("#")
    with open(path) as handle:
        data = handle.read()
        doc = yaml.load(data)

    if "$graph" in doc:
        graph = []
        for idoc in doc["$graph"]:
            idoc = prep_doc(idoc)
            if idoc['class'] == "CommandLineTool":
                graph.append( {"commandline" : idoc} )
            if idoc['class'] == "ExpressionTool":
                graph.append( {"expression" : idoc} )
            if idoc['class'] == "Workflow":
                graph.append( {"workflow" : idoc} )
        if resolve:
            rgraph = []
            for idoc in graph:
                if 'workflow' in idoc:
                    idoc['workflow'] = resolve_Workflow(idoc['workflow'], path, graph)
                rgraph.append(idoc)
            graph = rgraph
        newdoc = { "cwlVersion" : doc['cwlVersion'], "graph" : graph }
        #print json.dumps(newdoc, indent=4)
        out = GraphRecord()
        ParseDict(newdoc, out)
    else:
        doc = prep_doc(doc)
        if doc['class'] == "CommandLineTool":
            out = CommandLineTool()
        if doc['class'] == "ExpressionTool":
            out = ExpressionTool()
        if doc['class'] == "Workflow":
            if resolve:
                doc = resolve_Workflow(doc, path, [])
            out = Workflow()
        try:
            ParseDict(doc, out)
        except ParseError, e:
            sys.stderr.write("In doc:\n%s\n" % json.dumps(doc, indent=4))
            sys.stderr.write("Error: %s" % (e))
            raise e
    return out

def load_proto(path):
    with open(path) as handle:
        data = handle.read()
    doc = yaml.load(data)
    if doc['class'] == "CommandLineTool":
        out = CommandLineTool()
    if doc['class'] == "ExpressionTool":
        out = ExpressionTool()
    if doc['class'] == "Workflow":
        out = Workflow()
    ParseDict(doc, out)
    return out

def to_dict(pb):
    return MessageToDict(pb)

############################

def cwl_TypeRecord(pb):
    if pb.WhichOneof("type") == "name":
        return pb.name
    if pb.WhichOneof("type") == "array":
        out = {"type" : "array", "items" : cwl_TypeRecord( pb.array.items ) }
        i = to_dict(pb.inputBinding)
        if len(i) > 0:
            out["inputBinding"] = i
        return out
    if pb.WhichOneof("type") == "oneof":
        out = []
        for i in pb.oneof.types:
            out.append(cwl_TypeRecord(i))
        return out
    if pb.WhichOneof("type") == "enum":
        return { "name" : pb.enum.name, "symbols" : pb.enum.symbols }

def cwl_DataRecord(pb):
    if pb.WhichOneof("data") == "string_value":
        return pb.string_value
    if pb.WhichOneof("data") == "float_value":
        return pb.float_value
    if pb.WhichOneof("data") == "int_value":
        return pb.int_value
    if pb.WhichOneof("data") == "bool_value":
        return pb.bool_value
    if pb.WhichOneof("data") == "list_value":
        return to_dict(pb.list_value)
    if pb.WhichOneof("data") == "struct_value":
        return to_dict(pb.struct_value)

def cwl_ExpressionTool(pb):
    doc = to_dict(pb)
    inputs = []
    for i in pb.inputs:
        inputs.append(to_cwl(i))
    doc['inputs'] = inputs
    outputs = []
    for i in pb.outputs:
        outputs.append(to_cwl(i))
    doc['outputs'] = outputs

    return doc

def cwl_Workflow(pb):
    return to_dict(pb)

def cwl_CommandLineTool(pb):
    doc = to_dict(pb)
    inputs = []
    for i in pb.inputs:
        inputs.append(to_cwl(i))
    doc['inputs'] = inputs
    outputs = []
    for i in pb.outputs:
        outputs.append(to_cwl(i))
    doc['outputs'] = outputs

    return doc


def cwl_InputParameter(pb):
    doc = to_dict(pb)
    if 'type' in doc:
        doc['type'] = cwl_TypeRecord(pb.type)
    return doc

def cwl_OutputParameter(pb):
    doc = to_dict(pb)
    if 'type' in doc:
        doc['type'] = cwl_TypeRecord(pb.type)
    return doc

def cwl_CommandInputParameter(pb):
    doc = to_dict(pb)
    if 'type' in doc:
        doc['type'] = cwl_TypeRecord(pb.type)
    if 'default' in doc:
        doc['default'] = cwl_DataRecord(pb.default)
    return doc

def cwl_CommandOutputParameter(pb):
    doc = to_dict(pb)
    if 'type' in doc:
        doc['type'] = cwl_TypeRecord(pb.type)
    return doc

PB2CWL = {
    "Workflow" : cwl_Workflow,
    "CommandLineTool" : cwl_CommandLineTool,
    "ExpressionTool" : cwl_ExpressionTool,
    "InputParameter" : cwl_InputParameter,
    "OutputParameter" : cwl_OutputParameter,
    "CommandInputParameter" : cwl_CommandInputParameter,
    "CommandOutputParameter" : cwl_CommandOutputParameter,
    "ExpressionToolOutputParameter" : cwl_OutputParameter
}

def to_cwl(pb):
    return PB2CWL[pb.DESCRIPTOR.name](pb)
