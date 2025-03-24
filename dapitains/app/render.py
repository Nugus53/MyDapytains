from dapitains.constants import PROCESSOR,get_xquery_proc,get_xpath_proc, saxonlib
from dapitains.app.database import db, Collection, Navigation
import re
import importlib.util
import os
import json
try:
    import uritemplate
    from flask import Flask, request, Response
    from flask_sqlalchemy import SQLAlchemy
    import click
except ImportError:
    print("This part of the package can only be imported with the web requirements.")
    raise


from urllib.parse import urlparse

def msg_4xx(string, code=404) -> Response:
    return Response(json.dumps({"message": string}), status=code, mimetype="application/json")

def is_url(path):
    result = urlparse(path)
    return all([result.scheme, result.netloc])

def check_url(path, autoriser_lien_externe=True, liste_hotes=None):
    if is_url(path):
        if autoriser_lien_externe:
            if liste_hotes:
                host = urlparse(path).netloc
                if host in liste_hotes: 
                    return True
                else:
                    return False 
            else:
                return True 
        else:
            return True
    else:
        return True 
    
def render(identifier,content,mediatype):
    try :
        transform=get_all_transform(identifier)
    except:
        transform=None

    try :
        mediatype=mediatype.replace("'","")
    except:
        mediatype=None
    
    if mediatype ==None :
        return Response(content, mimetype="application/xml")
    elif mediatype not in transform.keys() :
            
            return msg_4xx(f"Unknown transform process`{mediatype}` for `{identifier}`")
    else :
            if transform[mediatype]['method'] == 'text/xsl':
                return Response(Xslt(content,transform[mediatype]['href']), mimetype=mediatype)
            if transform[mediatype]['method'] == 'text/xq':
                return Response(Xquery(content,transform[mediatype]['href']), mimetype=mediatype)
            if transform[mediatype]['method'] == 'text/py':
                return Response(Python(content,transform[mediatype]['href']), mimetype=mediatype)
            else :
                return msg_4xx(f"Unknown`{transform[mediatype]['method']}` method process ")

        
def get_all_transform(identifier):
    rslt={}
    for list in [get_col_transform(identifier,True),get_doc_transform(identifier)]:
        rslt=merge(rslt,list,'use-first')
    return rslt


def merge(listSource,ListAdd,method):
    for key in ListAdd.keys():
        if key in listSource.keys():
            if method=='use-first':
                pass
            if method=='use-last':
                listSource[key]=ListAdd[key]
            if method=='rejet':
                listSource.pop(key)
        else :
            listSource[key]=ListAdd[key]
            print('add')
    return listSource

# A ajouter
# def get_inst_transform():

# on pourai également ajouter :
#ajouter à l'instance regler par namespace
#ajouter à l'instance regler par metadata 


def get_col_transform(identifier:str, recursive: bool= False):
    """ 
    Retrieve transformation information declared at the collection level.

    This function retrieves metadata related to a resource or collection specified by its identifier.
    If the 'recursive' option is enabled, the retrieval may include nested elements or collections.

    :param identifier: The tag of the collection or resource to retrieve (as a string).
    :type identifier: str
    :param recursive: A flag indicating whether to include nested elements or collections (default is False).
    :type recursive: bool, optional
    :returns: An object containing the main metadata, either for a resource or a collection.
    :rtype: Union[Resource, Collection]  # Adjust this type according to what is returned (Resource, Collection, or other)
    
    """
    coll = Collection.query.where(Collection.identifier == identifier).first()
    returnList = {}
    boucleCheck=[]
    method='use-first'
    
    def recursive_add(parents,returnList,boucleCheck):
        for p in parents:
            if p.identifier not in boucleCheck:
                boucleCheck.append(p.identifier)
                returnList=merge(returnList,p.mediatype,method)
                if recursive and hasattr(p, 'parents') and p.parents:
                    recursive_add(p.parents,returnList,boucleCheck)

    recursive_add(coll.parents,returnList,boucleCheck)
    return returnList
  
    
def get_doc_transform(identifier):
    coll = Collection.query.where(Collection.identifier == identifier and Collection.resource==True).first()
    xml=PROCESSOR.parse_xml(xml_file_name=coll.filepath)
    xpath = get_xpath_proc(elem=xml).evaluate("/processing-instruction('xml-stylesheet')/string()")
    returnList={}
    if xpath is not None:
        for rsl in iter(xpath):
            info={}
            for item in re.split(r'\s+', rsl.string_value.strip()):
                man = item.split('=')
                if len(man) == 2:  
                    field = man[0].strip()
                    value = man[1].strip().strip('"').strip("'")
                    info[field]=value
            
            required_keys = ['type', 'href', 'dapytains:mediatype']
            if all(key in info for key in required_keys):
                dic={info['dapytains:mediatype']:{'method':info['type'],'href':info['href']}}
                returnList=merge(returnList,dic,'use-first')
            else:
                print(info)
    
    return returnList




def Xslt(content,render):
    xml=PROCESSOR.parse_xml(xml_text=content)
    test= get_xpath_proc(elem=xml).evaluate(f'''
    transform(  map {{
    "stylesheet-location" : "{render}",
    "source-node": .
    }})?output
    ''')
    return str(test)

# ajouter d'autres outils de transformation :
#def ODD():
def Xquery(content,render):
    xml=PROCESSOR.parse_xml(xml_text=content)
    test= get_xquery_proc(elem=xml)
    test.set_query_file(render)
    return test.run_query_to_string(query_file=render)

def Python(content,render):
    xml=PROCESSOR.parse_xml(xml_text=content)

    module_name = os.path.splitext(os.path.basename(render))[0]
    
    spec = importlib.util.spec_from_file_location(module_name, render)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if not hasattr(module, "Handler"):
        raise AttributeError(f"La fonction 'Handler' n'existe pas dans '{render}'.")

    function = getattr(module, 'Handler')
    return function(xml)



