@echo off
MODE CON: COLS=132 LINES=40

::Parameters to adapt to each analysis env :
Set SourceFolder=C:\Oxygenworkspacedb2sqlservermigrationnew\com.castsoftware.labs.db2sqlservermigration\DevTools
Set TargetFolder=C:\Oxygenworkspacedb2sqlservermigrationnew\com.castsoftware.labs.db2sqlservermigration\MasterFiles
Set adgMetrics=AdgMetrics_db2sqlservermigration.xml

::Parameters to adapt in some cases :
Set MetricsCompiler_BAT_path=.\MetricsCompiler.bat


Title Generating %adgMetrics% from MASTER FILES at %TargetFolder%

:: call Compiler - full syntax (with specific AdgConfigData file name)
call %MetricsCompiler_BAT_path% -encodeUA -inputdir %TargetFolder% -outputdir %SourceFolder% -filename %adgMetrics%

::TOBE : Manage ERRORLEVEL ?
pause