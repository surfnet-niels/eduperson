#! /bin/python3

import sys
import json
from pathlib import Path


def loadJSON(json_file):
   with open(json_file) as json_file:
     return json.load(json_file)

def p(message, writetolog=False):
   if writetolog:
      write_log(message)
   else:
      print(message)
    
def pj(the_json, writetolog=False):
    p(json.dumps(the_json, indent=4, sort_keys=False), writetolog)


def write_file(contents, filepath, mkpath=True, overwrite=False, type='txt'):
   if mkpath:
      Path(filepath).mkdir(parents=True, exist_ok=overwrite)

   if overwrite:
      f = open(filepath, "w")
   else:
      f = open(filepath, "a")

   match type:
    case 'yaml':
         yaml.preserve_quotes = True
         yaml.dump(contents, f)
    case 'json':
         f.write(json.dumps(contents,sort_keys=False, indent=4, ensure_ascii=False,separators=(',', ':')))
    case _:
         # assume text
         f.write(contents+"\n")
   
   f.close()

def replace_capitals(s):
    return ''.join(['' + ("_" + char.lower()) if char.isupper() else char for char in s]).strip()

def covert_schemaname(attributeName):
   # Attributes need to be rename to claims
   # as a general rule of thumb:
   #
   # eduPerson, voPerson and Schac schema names are just lowercased ad get added an underscore
   #
   # for the attrbute name: if a captical is found, it is replaced with a lower and prefixed with an underscore.
   #
   # sp eduPersonScopedAffiliation becomes: eduperson_scoped_affiliation
   # 
   s= attributeName

   if s.startswith('eduPerson'):
      return ("eduperson" + replace_capitals(s[9:]).replace("_i_d", "_id").replace("_d_n", "_dn"))
   elif s.startswith('voPerson'):
      return ("voperson" + replace_capitals(s[7:]).replace("_i_d", "_id").replace("_d_n", "_dn"))
   elif s.startswith('Schac'):
      return ("schac" + replace_capitals(s[5:]).replace("_i_d", "_id").replace("_d_n", "_dn"))
   else:
      return (replace_capitals(s).replace("_u_r_i", "_uri").replace("_s_m_i_m_e", "_smime"))
   
def main(argv):
   schemaFile = "eduPerson_202208_v4_4_0.json"

   schema = { 
      "$id": "https://refeds.org/schemas/vc/eduPerson_202208_v4_4_0.json",
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "$comment": "This schema implements the eduPerson schema version 4.4.0 (2022-08) - https://wiki.refeds.org/display/STAN/eduPerson+%28202208%29+v4.4.0. This schema is maintained by REFEDs (https://refeds.org). The mission of REFEDS (the Research and Education FEDerations group) is to be the voice that articulates the mutual needs of research and education identity federations worldwide.",
      "title": "eduPersonCredential",
      "description": "Schema for verifiable credential claims describing a user in the context of eduPerson",
      "type": "object",
      "properties": {
         "credentialSubject": {
            "type": "object",
            "properties": {}
         }
      }
   }

   # Generate object properties based on SCIM schema proposal from marcvs (https://github.com/marcvs) 
   # https://github.com/REFEDS/eduperson/pull/25
   #
   # the file from the scim schema was added temporarily as the pull request is not yet accepted in the main branch
   #
   # TODO: base this on eduperson-202208.md file
   #
   scimSchema = loadJSON('eduperson_schema.json')
   object_props = {}
   att = scimSchema['attributes']

   for i in range(len(att)):
      name = covert_schemaname(att[i]['name'])

      object_props[name] = {
         "type": att[i]['type'],
         "description": att[i]['description'],
      }
      # handle enums
      if 'canonicalValues' in att[i].keys():
         object_props[name]['enum'] = att[i]['canonicalValues']

      # TODO: validate these
      # TODO: we still have several format and pattern definitions missing
      match att[i]['name']:
         case "mail":
            object_props[name]['format'] = "email"

         case "eduPersonEntitlement":
            object_props[name]['format'] = "uri"

         case "eduPersonPrincipalName" | "eduPersonPrincipalNamePrior" | "eduPersonScopedAffiliation":
            object_props[name]['pattern'] = "^\\S+@\\S+\\.\\S+$"
         
         case "eduPersonTargetedID":
            object_props[name]['description'] = 'A persistent, non-reassigned, opaque identifier for a principal.'
            object_props[name]['deprecated'] = True

         case "eduPersonAssurance" | "labeledURI":
            object_props[name]['type'] = "array"
            object_props[name]['anyof'] =  { "type": "uri" }
      
         case "homePhone" | "facsimileTelephoneNumber" | "mobile" | "pager" | "telephoneNumber":
            object_props[name]['type'] = "array"
            object_props[name]['anyof'] =  {
               "type": ["string", "null"],
               "minLength": 10,
               "maxLength": 20,
               "pattern": "^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"
               }

   schema["properties"]["credentialSubject"]["properties"] = object_props

   write_file(schema, schemaFile, mkpath=False, overwrite=True, type='json')

if __name__ == "__main__":
   main(sys.argv[1:])