<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- Identity template to copy all nodes -->
    <!--<xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>-->
    <xsl:template match="*:TEI">
        <html>
            <head>
            <xsl:apply-templates select="./*:teiHeader"/>
            </head>
            <body>
            <xsl:apply-templates select="./*:text"/>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="*:div">
        <div>
            <xsl:apply-templates select="node()"/>
        </div>
    </xsl:template>

    
    <xsl:template match="*:p">
        <p>
            <xsl:apply-templates select="node()"/>
        </p>
    </xsl:template>

</xsl:stylesheet>
