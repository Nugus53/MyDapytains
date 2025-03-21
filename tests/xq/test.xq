xquery version "3.0";
declare option saxon:output "method=text";
declare function local:transform($node as node()) {
    
   
normalize-space($node/string())
 
};


let $xml := .
return local:transform($xml)
