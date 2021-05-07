import cast_upgrade_1_6_5 # @UnusedImport
from cast.application import ApplicationLevelExtension, ReferenceFinder
import logging
import xml.etree.ElementTree as ET
import re
import os
import random
from html import unescape
from pathlib import Path


class db2sqlservermigrationExtensionApplication(ApplicationLevelExtension):

    def __init__(self): 
        self.currentsrcfile=""
        self.sregex = ""
        self.sgobjname=""
        self.filename = ""
        self.xmlfile = ""
        self.file = ""    
        self.propvalue=[]
        self.uniqueobjlist =[]
        pass     
     
        
        
    def end_application(self, application):
        logging.debug("running code at the end of an application in db2sqlservermigration")
        self.setdeclareproperty(application);
        s= self.get_plugin()
        #logging.info(str(s.get_plugin_directory()))
        try:
            self.xmlfile =str(s.get_plugin_directory())+ "\\parsedefine.xml" 
            if (os.path.isfile(self.xmlfile)):
                        tree = ET.parse(self.xmlfile, ET.XMLParser(encoding="UTF-8"))
                        root=tree.getroot()
            logging.debug(str(self.xmlfile));
        except ET.ParseError as err:
            logging.info(": error  saving property violation   : %s", str(err))  
            return tree
        for o in application.search_objects(category='sourceFile'):
          
            # check if file is analyzed source code, or if it generated (Unknown)
            if not o.get_path():
                continue
           
            if not (o.get_path().endswith('.sql')):
                continue
            #cast.analysers.log.debug("file found: >" + str(o.get_path()))
            logging.debug("file found: >" + str(o.get_path()))
            self.sqljavacsfilesearch(o, application, root, 'Search', 'sql') 
            #self.scan_Sql(application, o)               
        
        for o in application.search_objects(category='JV_FILE'):
     
            # check if file is analyzed source code, or if it generated (Unknown)
            if not o.get_path():
                continue
            
            if not (o.get_path().endswith('.java')):
                continue
            #cast.analysers.log.debug("file found: >" + str(o.get_path()))
            logging.debug("file found: >" + str(o.get_path()))
             
            if (o.get_path().endswith('.java')):  
                self.sqljavacsfilesearch(o, application, root, 'javafileSearch', 'java') 
                
        for o in application.search_objects(category='CAST_DotNet_CSharpFile'):
            # check if file is analyzed source code, or if it generated (Unknown)
            if not o.get_path():
                continue
            
            if not (o.get_path().endswith('.cs')):
                continue
            #cast.analysers.log.debug("file found: >" + str(o.get_path()))
            logging.debug("file found: >" + str(o.get_path()))
             
            if (o.get_path().endswith('.cs')):  
                self.sqljavacsfilesearch(o, application, root, 'csharpfileSearch', 'cs')  
                
        for o in application.search_objects(category='sourceFile'):
           
            # check if file is analyzed source code, or if it generated (Unknown)
            if not o.get_path():
                continue
            
            if not (o.get_path().endswith('.properties')):
                continue
            #cast.analysers.log.debug("file found: >" + str(o.get_path()))
            logging.debug("file found: >" + str(o.get_path()))
         
            if (o.get_path().endswith('.properties')):
                self.getpropertiessearch(o, application, root)
                  
                
    
        
    def getpropertiessearch(self,  file, application, root): 
        logging.info("Properties java start")
       
        try:
                    for group in root.findall('propertiesfileSearch'):
                        self.sregex = unescape(group.find('RegexPattern').text)
                        logging.debug("---"+str(self.sregex)+ "---")
                                   
                        if file.get_name().endswith('.properties'):
                            logging.info('Scanning properties  file :'+str(Path(file.get_path()).name))
                            if (os.path.isfile(file.get_path())):
                                sobjname = group.find('propertyname').text 
                                self.currentsrcfile= file
                                self.sgobjname=sobjname
                                sviolation = group.find('Rulename').text 
                                logging.debug(str(sobjname)+"Reg ex--->"+str(self.sregex) )
                                self.setprop(application, file, sobjname, sviolation); 
                                
        except Exception as e:
            logging.info(": error  db2Sql extension  properties search  : %s", str(e))  
            return 
        
   
        
    def sqljavacsfilesearch(self,  file, application, root,tag,fileext): 
        logging.info("file start")
       
        try:
                    for group in root.findall(tag):
                        self.sregex = unescape(group.find('RegexPattern').text)
                        logging.debug("---"+str(self.sregex)+ "---")
                                   
                        if file.get_name().endswith('.'+fileext):
                            logging.info('Scanning '+fileext+ '  file :'+str(Path(file.get_path()).name))
                            if (os.path.isfile(file.get_path())):
                                sobjname = group.find('propertyname').text 
                                self.currentsrcfile= file
                                self.sgobjname=sobjname
                                sviolation = group.find('Rulename').text 
                                logging.debug(str(sobjname)+"Reg ex--->"+str(self.sregex) )
                                self.sqljavacsharp(application, file, sobjname, sviolation); 
                                
        except Exception as e:
            logging.info(": error  db2Sql extension  file search  set : %s", str(e))  
            return  
              
        
        
    def sqljavacsharp(self, application, file, sobjname, rulename):
            # one RF for multiples patterns
            
            rfCall = ReferenceFinder()
            rfCall.add_pattern(('srcline'),before ='' , element =self.sregex, after = '')     # requires application_1_4_7 or above
            
            # search all patterns in current program
            try:
                self.propvalue =[]
                self.uniqueobjlist =[]
                cntj= 0
                references = [reference for reference in rfCall.find_references_in_file(file)]
                for  reference in references:
                    reference.bookmark.file= file
                    linenb=int(str(reference.bookmark).split(',')[2])
                    #logging.debug( str(reference.bookmark).split(',')[2])
                    #logging.debug("Specific object:"+ str(file.find_most_specific_object(linenb, 1)))
                    obj = file.find_most_specific_object(linenb, 1)
                    cntj =cntj+1
                    self.uniqueobjlist.append(sobjname + "cast" +str(obj))
                    obj.save_violation('dbsqlservermigration_CustomMetrics.'+ rulename, reference.bookmark)
                    logging.debug("violation saved: >" +'dbsqlservermigration_CustomMetrics.'+rulename+"  line:::"+str(reference.value)+str(reference.bookmark))
                            #break
#                     file.save_property('dbsqlservermigrationScript.'+sobjname, reference.value+" "+str(reference.bookmark) )
#                     logging.info("property saved: >" +'dbsqlservermigrationScript.'+sobjname +" "+str(reference.bookmark)+ ' '+ str(reference.value))
                                #logging.info('unique' + str(self.uniqueobjlist))
                self.unique(self.uniqueobjlist,application)
                     
            except Exception as e:
                logging.info(": error  saving property violation   : %s", str(e))  
                return 
#       
            except Exception as e:
                logging.info(": error  saving property violation   : %s", str(e))  
                return 
            
    # function to get unique values
    def unique(self, objcastlist, application):
       
        unique_list = []
        #logging.info(str(objcastlist))
       
       
        for x in objcastlist:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)
                  
        for x in unique_list:
            logging.debug('{} has occurred {} times'.format(x, self.countcastobject(objcastlist, x)))
            logging.debug(x)
            orgx=x
            x= x.replace('castObject', ',')
            x= x.replace('castFile', ',')
            x=x.replace('(', '')
            x= x.replace(')', '')
            dbtype = x.split(',')[0].strip()
            objname= x.split(',')[1].strip()
            objcatergory =x.split(',')[2].strip()
            
            if objname.find('.') is not -1:
                if objcatergory.find('sourceFile') is not  -1:
                    objname = objname
                else:
                    objname = objname.split('.')[1]
            MethodObjectReferences = list(application.search_objects(category=objcatergory,  name=objname,  load_properties=True))
            if len(MethodObjectReferences)>0:
                for obj in MethodObjectReferences : 
                    cnt = str(self.countcastobject(objcastlist, orgx))
                    obj.save_property('dbsqlservermigrationScript.'+dbtype, cnt)
                    logging.debug("property saved: --->" +'dbsqlservermigrationScript.'+dbtype +" "+cnt)  
                            
    def countcastobject(self, lst, x):
        count = 0
        for ele in lst:
            if (ele == x):
                count = count + 1
        return count 
    
    def setprop(self, application, file, sobjname, rulename):
            # one RF for multiples patterns
            
            rfCall = ReferenceFinder()
            rfCall.add_pattern(('srcline'),before ='' , element =self.sregex, after = '')     # requires application_1_4_7 or above
            
            # search all patterns in current program
            try:
#                 self.propvalue =[]
                getvalue=""
                cntprop= 0
                references = [reference for reference in rfCall.find_references_in_file(file)]
                for  reference in references:
                    reference.bookmark.file= file
                    cntprop =cntprop+1
                    #self.propvalue.append(str(reference.value)+" "+str(reference.bookmark))
                    file.save_violation('dbsqlservermigration_CustomMetrics.'+ rulename, reference.bookmark)
                    logging.debug("violation saved: >" +'dbsqlservermigration_CustomMetrics.'+rulename+"  line:::"+str(reference.value)+str(reference.bookmark))
                            #break
#                     file.save_property('dbsqlservermigrationScript.'+sobjname, reference.value+" "+str(reference.bookmark) )
#                     logging.info("property saved: >" +'dbsqlservermigrationScript.'+sobjname +" "+str(reference.bookmark)+ ' '+ str(reference.value))
                getvalue=str(cntprop)
                #logging.debug("Value of list-->"+ str(getvalue))
                if cntprop >0:
                    file.save_property('dbsqlservermigrationScript.'+sobjname, getvalue)
                    logging.debug("property saved: --->" +'dbsqlservermigrationScript.'+sobjname +" "+getvalue)
               
#       
            except Exception as e:
                logging.info(": error  saving property violation on properties  : %s", str(e))  
                return 
            
    
    def setdeclareproperty(self, application):
        
        declarelist=['sourceFile', 'SQLScriptSchema','SQLScriptTable','SQLScriptTableColumn','SQLScriptIndex',
                     'SQLScriptProcedure','SQLScriptDML','SQLScriptFunction','SQLScriptView','SQLScriptTrigger',
                     'SQLScriptPackage','SQLScriptType','SQLScriptForeignKey','SQLScriptUniqueConstraint','SQLScriptEvent',
                     'SQLScriptSynonym','SQLScriptTableSynonym','SQLScriptViewSynonym','SQLScriptFunctionSynonym',
                     'SQLScriptProcedureSynonym','SQLScriptPackageSynonym','SQLScriptTypeSynonym','SQLScriptMethod','JV_METHOD', 'JV_GENERIC_METHOD', 
                     'JV_INST_METHOD', 'JV_INST_CLASS', 'JV_CTOR', 'JV_GENERIC_CTOR', 'JV_FILE', 'JV_INST_CTOR', 'JV_INTERFACE', 'JV_GENERIC_INTERFACE', 
                     'JV_INST_INTERFACE', 'JV_GENERIC_CLASS','JV_PROJECT', 'JV_PACKAGE', 'JV_CLASS','CAST_DotNet_InterfaceCSharp','CAST_DotNet_GenericInterfaceCSharp','CAST_DotNet_InstantiatedGenericInterfaceCSharp',
                     'CAST_DotNet_StructureCSharp','CAST_DotNet_GenericStructureCSharp','CAST_DotNet_InstantiatedGenericStructureCSharp','CAST_DotNet_InstantiatedGenericDelegateCSharp',
                        'CAST_DotNet_ClassCSharp','CAST_DotNet_ClassCSharpException', 'CAST_DotNet_ClassCSharpCustomAttribute','CAST_DotNet_ClassCSharpDataSet','CAST_DotNet_ClassCSharpUserControl',
                        'CAST_DotNet_ClassCSharpForm','CAST_DotNet_ClassCSharpCustomControl','CAST_DotNet_ClassCSharpComponent','CAST_DotNet_ClassCSharpServiceBase','CAST_DotNet_ClassCSharpServicedComponent',
                        'CAST_DotNet_ClassCSharpInstaller','CAST_DotNet_ClassCSharpWebService','CAST_DotNet_ClassCSharpWebServiceProxy','CAST_DotNet_ClassCSharpCrystalReportClass','CAST_DotNet_GenericClassCSharp',
                        'CAST_DotNet_InstantiatedGenericClassCSharp','CAST_DotNet_EventCSharp','CAST_DotNet_MethodCSharp','CAST_DotNet_GenericMethodCSharp','CAST_DotNet_InstantiatedGenericMethodCSharp',
                        'CAST_DotNet_ConstructorCSharp','CAST_DotNet_DestructorCSharp','CAST_DotNet_CSharpObject','CAST_DotNet_CSharpGroupMethod','CAST_DotNet_CSharpGroupControl','CAST_DotNet_CSharpGroupConfig',
                        'CAST_DotNet_CSharpFile', 'CAST_DotNet_UsingNamespaceDirectiveCSharp','CAST_DotNet_UsingAliasDirectiveCSharp']
        for declareitems in declarelist: 
                application.declare_property_ownership('dbsqlservermigrationScript.CONCAT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATEADD',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.BLOB',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.CLOB',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DBCLOB',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DECFLOAT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DOUBLE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.GRAPHIC',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.LONG_VARCHAR',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NCLOB',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.TIMESTAMP',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARGRAPHIC',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NUM',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.CHAR',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.CURRENT_DATE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.INT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.LOCATE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.SMALLHINT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.SUBSTR',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.USER',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.SYSDUMMY',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.FOR_READ_ONLY',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.WITH_UR',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.BUFFERPOOL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.INDEXBP',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.STOGROUP',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.UNICODE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.FOR_BIT_DATA',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.MIXED_DATA',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.IN_TABLESPACE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.EBCDIC',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.CHANGES',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.ALL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.WITH_RESTRICT_ON_DROP',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VOLATILE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VALUEYES',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARCHAR',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.INTEGER',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DECIMAL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NUMERIC',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATE_WITH_DEFAULT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.TIMESTAMP_WITH_DEFAULT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.PICTFREE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VALUENO',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.FREEPAGE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.BUFFERPOOL_Zos',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NONE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NOT_CLUSTER',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.YES_zos',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NO_zos',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.PIECESIZE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NOT_PADDED',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.PRIQTY',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.SECQTY',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.YES_STOGROUP',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.MICROSECOND',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NOT_DETERMINSTIC',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.LANGUAGE_SQL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.CONTAINS_SQL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NO_SQL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.READS_SQL_DATA',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.MODIFIES_SQL_DATA',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.SPECIFIC',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.CALLED_ON_NULL_INPUT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.INHERIT_SPECIAL_REGISTERS',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NO_EXTERNAL_ACTION',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.STRIP',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.TIMEStamp',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.TIMESTAMPDIFF',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.TRUNC_TIMESTAMP',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.TRUNCATE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.UCASE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VALUE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARCHAR_Buildin',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARCHAR_BIT_FORMER',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARCHAR_FORMAT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARCHAR_FORMAT_BIT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARGRAPHIC_Buildin',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.WEEK',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.XMLDOCUMENT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.XMLNAMESPACES',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.XMLROW',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.XMLTEXT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.XMLVALIDATE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.XMLXMLXSROBJECTID',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.YEAR_Builin',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPEBIGINT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.CHAR_FOR_BIT_DATA',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.CHAACTER_VARYING',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPEDBCLOB',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPEDECIMAL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPEDECFLOAT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPEFLOAT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPEGRAPHIC',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.INTEGER_Datatype',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NCHAR_VARYING',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NUMERIC_Dattype',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.REAL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.SMALLINT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPETIME',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPEVARCHAR',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARCHAR_FOR_BIT_DATA',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATATYPEVARGRAPHIC',[declareitems])
                #Custom metrics 11 rules
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.SQL_language_elements',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.Data_type_mapping',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.Db2_SQL_functions',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.SQL_SELECT_statement',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.CREATE_DATABASE_statement',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.CREATE_TABLE_statement',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.INDEX_statement',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.stored_procedures',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.user_defined_functions',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.procedural_SQL_statements',[declareitems])
                application.declare_property_ownership('dbsqlservermigration_CustomMetrics.SQL_statements',[declareitems])
               