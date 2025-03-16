from dapitains.constants import PROCESSOR,get_xpath_proc, saxonlib
from dapitains.app.database import db, Collection, Navigation
import re
 
# Note 
# ajouter la récupération du chemin absolue du fichier de Transformation
# Pour des question de sécuriter 
# autoriser ou non les transformation venant d'une url
# autoriser uniquement venant de certains HOST
# external_url=True

def get_all_transform(identifier):
    rslt={}
    for list in [get_col_transform(identifier,True),get_doc_transform(identifier)]:
        rslt=merge(rslt,list,'use-first')
    return rslt


def merge(listSource,ListAdd,method):
    for key in ListAdd.keys():
        if key in listSource.keys():
            if method=='use-first':
                print('test')
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




def Xslt(identifier,render):
    coll = Collection.query.where(Collection.identifier == identifier and Collection.resource==True).first()
    xml=PROCESSOR.parse_xml(xml_file_name=coll.filepath)
    test= get_xpath_proc(elem=xml).evaluate(f'''
    transform(  map {{
    "stylesheet-location" : "{render}",
    "source-node": .
    }})?output
    ''')
    return str(test)

# ajouter d'autres outils de transformation :
#def ODD():
#def Xquery():
#def Python():