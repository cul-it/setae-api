<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <item>
      <xsl:choose>
        <xsl:when test="error">
          <error>
            <xsl:value-of select="error" />
          </error>
          <bib_data>
            <title>ERROR</title>
          </bib_data>
          <holding_data>
            <call_number_type desc="Superintendent of Documents classification">3</call_number_type>
            <call_number>
              <xsl:value-of select="error" />
            </call_number>
          </holding_data>
          <item_data>
            <description>ERROR</description>
            <library desc="ERROR">ERROR</library>
            <location desc="ERROR">ERROR</location>
          </item_data>
        </xsl:when>
        <xsl:otherwise>
          <bib_data>
            <mms_id></mms_id>
            <title>
              <xsl:value-of select="item/title"/>
            </title>
            <author>
              <xsl:for-each select="item/contributorNames/item"><xsl:value-of select="name"/>,</xsl:for-each>
            </author>
            <complete_edition></complete_edition>
            <network_numbers>
              <network_number></network_number>
            </network_numbers>
            <place_of_publication></place_of_publication>
            <date_of_publication></date_of_publication>
            <publisher_const></publisher_const>
          </bib_data>
          <holding_data>
            <holding_id>
              <xsl:value-of select="item/holdingsRecordId"/>
            </holding_id>
            <call_number_type desc="Library of Congress classification">0</call_number_type>
            <call_number>
              <xsl:value-of select="item/effectiveCallNumberComponents/callNumber"/>
            </call_number>
            <accession_number></accession_number>
            <copy_id>
              <xsl:value-of select="item/copyNumber"/>
            </copy_id>
            <in_temp_location>false</in_temp_location>
          </holding_data>
          <item_data>
            <pid>
              <xsl:value-of select="item/id"/>
            </pid>
            <barcode>
              <xsl:value-of select="item/barcode"/>
            </barcode>
            <creation_date>
              <xsl:value-of select="item/metadata/createdDate"/>
            </creation_date>
            <modification_date>
              <xsl:value-of select="item/metadata/updatedDate"/>
            </modification_date>
            <base_status>
              <xsl:attribute name="desc">
                <xsl:value-of select="item/status/name"/>
              </xsl:attribute>
              <xsl:text>1</xsl:text>
            </base_status>
            <awaiting_reshelving>false</awaiting_reshelving>
            <physical_material_type>
              <xsl:attribute name="desc">
                <xsl:value-of select="item/materialType/name"/>
              </xsl:attribute>
              <xsl:value-of select="item/materialType/name"/>
            </physical_material_type>
            <policy></policy>
            <provenance></provenance>
            <po_line></po_line>
            <is_magnetic></is_magnetic>
            <prefix>
              <xsl:value-of select="item/effectiveCallNumberComponents/prefix"/>
            </prefix>
            <suffix>
              <xsl:value-of select="item/effectiveCallNumberComponents/suffix"/>
            </suffix>
            <year_of_issue></year_of_issue>
            <enumeration_a>
              <xsl:value-of select="item/enumeration"/>
            </enumeration_a>
            <enumeration_b></enumeration_b>
            <enumeration_c></enumeration_c>
            <enumeration_d></enumeration_d>
            <enumeration_e></enumeration_e>
            <enumeration_f></enumeration_f>
            <enumeration_g></enumeration_g>
            <enumeration_h></enumeration_h>
            <chronology_i>
              <xsl:value-of select="item/chronology"/>
            </chronology_i>
            <chronology_j></chronology_j>
            <chronology_k></chronology_k>
            <chronology_l></chronology_l>
            <chronology_m>
              <xsl:value-of select="item/fund"/>
            </chronology_m>
            <description></description>
            <receiving_operator></receiving_operator>
            <process_type></process_type>
            <inventory_number></inventory_number>
            <inventory_price></inventory_price>
            <library>
              <xsl:attribute name="desc">
                <xsl:value-of select="item/effectiveLocation/name"/>
              </xsl:attribute>
              <xsl:value-of select="item/effectiveLocation/name"/>
            </library>
            <location>
              <xsl:attribute name="desc">
                <xsl:value-of select="item/effectiveLocation/name"/>
              </xsl:attribute>
              <xsl:value-of select="item/effectiveLocation/name"/>
            </location>
            <alternative_call_number></alternative_call_number>
            <alternative_call_number_type></alternative_call_number_type>
            <storage_location_id></storage_location_id>
            <pages></pages>
            <pieces>
              <xsl:value-of select="item/numberOfPieces"/>
            </pieces>
            <public_note></public_note>
            <fulfillment_note></fulfillment_note>
            <internal_note_1></internal_note_1>
            <internal_note_2></internal_note_2>
            <internal_note_3></internal_note_3>
            <statistics_note_1></statistics_note_1>
            <statistics_note_2></statistics_note_2>
            <statistics_note_3></statistics_note_3>
            <requested></requested>
            <edition></edition>
            <imprint></imprint>
            <language></language>
            <library_details>
              <address>
                <line1></line1>
                <line2></line2>
                <line3></line3>
                <line4></line4>
                <line5></line5>
                <city></city>
                <country></country>
                <email></email>
                <phone></phone>
                <postal_code></postal_code>
                <state></state>
              </address>
            </library_details>
            <parsed_alt_call_number/>
            <title_abcnph>
              <xsl:value-of select="item/title"/>
            </title_abcnph>
            <physical_condition/>
          </item_data>
        </xsl:otherwise>
      </xsl:choose>
    </item>
  </xsl:template>
</xsl:stylesheet>
