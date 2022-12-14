<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output indent="yes" method="xml"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    <data>
    <xsl:for-each select="SpimData/SequenceDescription/ViewSetups/ViewSetup">
       <row>
        <tile><xsl:apply-templates select="attributes/tile"/></tile>
        <imageName><xsl:apply-templates select="name"/></imageName>
       </row>
    </xsl:for-each>
    </data>

  </xsl:template>

</xsl:stylesheet>
