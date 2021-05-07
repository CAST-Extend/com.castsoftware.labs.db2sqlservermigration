<?xml version="1.0" encoding="iso-8859-1"?>
<Package PackName="ADG_LOCAL_db2sqlservermigration" Type="INTERNAL" Version="7.0.0.2" SupportedServer="ALL" Display="ADG on Local for db2sqlservermigration" DatabaseKind="KB_LOCAL" Description="">
	<Include>
	</Include>
	<Exclude>
	</Exclude>
	<Install>
	</Install>
	<Refresh>
		<Step Type="XML_MODEL" Option="4" File="set_tables.xml" Scope="db2sqlservermigrationScope">
		</Step>
	</Refresh>
	<Remove>
	</Remove>
</Package>