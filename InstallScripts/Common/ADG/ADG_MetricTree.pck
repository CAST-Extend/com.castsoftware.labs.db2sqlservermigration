<?xml version="1.1" encoding="UTF-8" ?>
<Package PackName="ADG_METRIC_TREE_db2sqlservermigration" Type="INTERNAL" Version="7.3.4.1" SupportedServer="ALL" Display="ADG Metric Tree for db2sqlservermigration" DatabaseKind="KB_CENTRAL" Description="">
	<Include>
	</Include>
	<Exclude>
	</Exclude>
	<Install>
    </Install>
	<Update>
    </Update>
	<Refresh>
		<Step Type="DATA" File="AdgMetrics_db2sqlservermigration.xml" Model="..\assessment_model_tables.xml" Scope="db2sqlservermigrationScope"></Step>
	</Refresh>
	<Remove>
	</Remove>
</Package>