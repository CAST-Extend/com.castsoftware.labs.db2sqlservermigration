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
            self.getconfigsearch(o, application, root)
            #self.scan_Sql(application, o)               
            
    def getconfigsearch(self,  file, application, root): 
        logging.info("file start")
       
        try:
                    for group in root.findall('Search'):
                        self.sregex = unescape(group.find('RegexPattern').text)
                        logging.debug("---"+str(self.sregex)+ "---")
                                   
                        if file.get_name().endswith('.sql'):
                            logging.info('Scanning sql  file :'+str(Path(file.get_path()).name))
                            if (os.path.isfile(file.get_path())):
                                sobjname = group.find('propertyname').text 
                                self.currentsrcfile= file
                                self.sgobjname=sobjname
                                sviolation = group.find('Rulename').text 
                                logging.debug(str(sobjname)+"Reg ex--->"+str(self.sregex) )
                                self.setprop(application, file, sobjname, sviolation); 
                                
        except Exception as e:
            logging.info(": error  db2Sql extension  set : %s", str(e))  
            return  
        # Final reporting in ApplicationPlugins.castlog
        
    def setprop(self, application, file, sobjname, rulename):
            # one RF for multiples patterns
            
            rfCall = ReferenceFinder()
            rfCall.add_pattern(('srcline'),before ='' , element =self.sregex, after = '')     # requires application_1_4_7 or above
            
            # search all patterns in current program
            try:
                self.propvalue =[]
                getvalue=""
                references = [reference for reference in rfCall.find_references_in_file(file)]
                for  reference in references:
                    reference.bookmark.file= file
                    linenb=int(str(reference.bookmark).split(',')[2])
                    #logging.debug( str(reference.bookmark).split(',')[2])
                    #logging.debug("Specific object:"+ str(file.find_most_specific_object(linenb, 1)))
                    obj = file.find_most_specific_object(linenb, 1)
                    self.propvalue.append(str(reference.value)+" "+str(reference.bookmark))
                    obj.save_violation('dbsqlservermigration_CustomMetrics.'+ rulename, reference.bookmark)
                    logging.debug("violation saved: >" +'dbsqlservermigration_CustomMetrics.'+rulename+"  line:::"+str(reference.value)+str(reference.bookmark))
                            #break
#                     file.save_property('dbsqlservermigrationScript.'+sobjname, reference.value+" "+str(reference.bookmark) )
#                     logging.info("property saved: >" +'dbsqlservermigrationScript.'+sobjname +" "+str(reference.bookmark)+ ' '+ str(reference.value))
                getvalue="".join(self.propvalue)
                #logging.debug("Value of list-->"+ str(getvalue))
                if len(getvalue) >0:
                    obj.save_property('dbsqlservermigrationScript.'+sobjname, str(getvalue))
                    #logging.info("property saved: --->" +'dbsqlservermigrationScript.'+sobjname +" "+str(getvalue))
               
#       
            except Exception as e:
                logging.info(": error  saving property violation   : %s", str(e))  
                return 
            
     
    
    def setdeclareproperty(self, application):
        
        declarelist=['sourceFile', 'SQLScriptSchema','SQLScriptTable','SQLScriptTableColumn','SQLScriptIndex',
                     'SQLScriptProcedure','SQLScriptDML','SQLScriptFunction','SQLScriptView','SQLScriptTrigger',
                     'SQLScriptPackage','SQLScriptType','SQLScriptForeignKey','SQLScriptUniqueConstraint','SQLScriptEvent',
                     'SQLScriptSynonym','SQLScriptTableSynonym','SQLScriptViewSynonym','SQLScriptFunctionSynonym',
                     'SQLScriptProcedureSynonym','SQLScriptPackageSynonym','SQLScriptTypeSynonym','SQLScriptMethod']
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
                application.declare_property_ownership('dbsqlservermigrationScript.YES',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.VARCHAR',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.INTEGER',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DECIMAL',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NUMERIC',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.DATE_WITH_DEFAULT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.TIMESTAMP_WITH_DEFAULT',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.PICTFREE',[declareitems])
                application.declare_property_ownership('dbsqlservermigrationScript.NO',[declareitems])
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
               