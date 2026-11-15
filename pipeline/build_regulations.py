"""Curated regulatory matrix. Every figure below was read from the cited PDF page of a loaded document.
Run: python pipeline/build_regulations.py  -> data/regulations.json
Pages are PDF page numbers. UR = Unrestricted."""
import json
from pathlib import Path
BBL, MDA, RP, EOI = "up_bbl_2025", "mda_mp2031_report", "ncrpb_rp2041", "ncrtc_tod_duhai_eoi"
RW = ["Road width", "Base FAR", "Max FAR"]
PURCH = ["Above base FAR is purchasable: up to 20% + 20% of base on roads up to 12 m, 50% + 50% on ≥12 to <24 m, 100% + 150% on ≥24 to <45 m, 100% + unrestricted on ≥45 m (purchasable + premium purchasable, §9.2.3, p.117).",
         "Purchasable FAR needs ROW of 12 m or more; 9 m for plotted residential and built-up group housing (§9.2.1, p.117).",
         "Fee = proportional land × circle rate × coefficient (§9.2.5, p.118–119). It is an enabling provision, not a right (§9.2.4, p.118).",
         "Green-rated buildings get 3%, 5% or 7% extra FAR free of cost, over and above the maximum (§9.3, p.119–120)."]
C = []
def card(id, doc, cat, scope, title, summary, uses=None, table=None, tables=None, conditions=(), incentives=(), cites=(), tod=False, quality=None):
    C.append(dict(id=id, doc_id=doc, category=cat, scope=scope, title=title, summary=summary, uses=uses,
                  tables=tables or ([table] if table else []), conditions=list(conditions), incentives=list(incentives),
                  cites=[dict(page=p, ref=r) for p, r in cites], requires_tod=tod, quality=quality))
T = lambda title, cols, rows: dict(title=title, columns=cols, rows=rows)

# ---------------- FAR / FSI ----------------
card("far_bbl_resplot", BBL, "far", "state", "Plotted residential", "Base FAR falls as plots get larger; the maximum is 2.25 to 2.50.", ["residential_plotted"],
     T("Plotted development, single or multi unit", ["Plot area (sq m)", "Base FAR", "Max FAR"],
       [["≥35 to <150", "2.0", "2.25"], ["≥150 to <300", "1.8", "2.50"], ["≥300 to <500", "1.75", "2.50"], ["≥500 to <1200", "1.5", "2.50"], ["≥1200", "1.25", "2.50"]]),
     conditions=["FAR is computed telescopically across the plot-size slabs (§3.2.2, p.49)."], incentives=PURCH[1:], cites=[(49, "§3.2.2.1"), (50, "§3.2.2.1"), (118, "§9.2.3")])
card("far_bbl_gh", BBL, "far", "state", "Group housing", "Base 1.50 in built-up areas and 2.50 elsewhere; the maximum rises with road width and is unrestricted on 45 m roads.", ["group_housing"],
     tables=[T("Group housing, built-up area", RW, [["≥9 to <12 m", "1.50", "2.10"], ["≥12 to <18 m", "1.50", "3.00"], ["≥18 to <24 m", "1.50", "3.00"], ["≥24 to <45 m", "1.50", "5.25"], ["≥45 m", "1.50", "UR"]]),
             T("Group housing, non-built-up area", RW, [["≥12 to <18 m", "2.50", "5.00"], ["≥18 to <24 m", "2.50", "5.00"], ["≥24 to <45 m", "2.50", "8.75"], ["≥45 m", "2.50", "UR"]]),
             T("Affordable group housing, built-up area", RW, [["≥9 to <12 m", "2.00", "2.40"], ["≥12 to <18 m", "2.00", "4.00"], ["≥18 to <24 m", "2.00", "4.00"], ["≥24 to <45 m", "2.00", "7.00"], ["≥45 m", "2.00", "UR"]]),
             T("Affordable group housing, non-built-up area", RW, [["≥12 to <18 m", "3.00", "6.00"], ["≥18 to <24 m", "3.00", "6.00"], ["≥24 to <45 m", "3.00", "9.00"], ["≥45 m", "3.00", "UR"]])],
     incentives=PURCH, cites=[(50, "§3.2.2.2")])
card("far_bbl_comm", BBL, "far", "state", "Commercial", "Base 1.50 to 3.00 depending on type and area; maximum by road width.", ["commercial"],
     tables=[T("Commercial units over 100 sq m, built-up area", RW, [["≥12 to <24 m", "1.50", "3.00"], ["≥24 to <45 m", "1.50", "5.00"], ["≥45 m", "1.50", "UR"]]),
             T("Commercial units over 100 sq m, non-built-up area", RW, [["≥12 to <24 m", "1.75", "3.50"], ["≥24 to <45 m", "1.75", "6.13"], ["≥45 m", "1.75", "UR"]]),
             T("Shopping malls, built-up area", RW, [["≥18 to <24 m", "2.00", "4.00"], ["≥24 to <45 m", "2.00", "7.00"], ["≥45 m", "2.00", "UR"]]),
             T("Shopping malls, non-built-up area", RW, [["≥18 to <24 m", "3.00", "6.00"], ["≥24 to <45 m", "3.00", "10.50"], ["≥45 m", "3.00", "UR"]])],
     incentives=PURCH, cites=[(50, "§3.2.2.3"), (51, "§3.2.2.3")])
card("far_bbl_office", BBL, "far", "state", "Office buildings", "Base 2.00 (built-up) or 2.50 (non-built-up); needs an 18 m road.", ["office"],
     tables=[T("Office buildings, built-up area", RW, [["≥18 to <24 m", "2.00", "4.00"], ["≥24 to <45 m", "2.00", "7.00"], ["≥45 m", "2.00", "UR"]]),
             T("Office buildings, non-built-up area", RW, [["≥18 to <24 m", "2.50", "5.00"], ["≥24 to <45 m", "2.50", "8.75"], ["≥45 m", "2.50", "UR"]])],
     incentives=PURCH, cites=[(53, "§3.2.2.3, item 15")])
card("far_bbl_ind", BBL, "far", "state", "Industrial", "Base 2.00 to 2.50 for industrial buildings and 3.00 for flatted factories, MSME and data centres.", ["industrial"],
     tables=[T("Industrial buildings (other than MSME)", RW, [["<12 m", "2.00", "2.00"], ["≥12 to <24 m", "2.50", "5.00"], ["≥24 to <45 m", "2.50", "8.75"], ["≥45 m", "2.50", "UR"]]),
             T("Flatted factories, MSME, data centres", RW, [["<12 m", "3.00", "3.00"], ["≥12 to <24 m", "3.00", "6.00"], ["≥24 to <45 m", "3.00", "10.50"], ["≥45 m", "3.00", "UR"]])],
     conditions=["Hostels and dormitories for workers are allowed up to 20% of FAR (§7.1.5, p.107).",
                 "Industry permitted in an agriculture zone gets 50% of the base FAR (Note-2, p.57)."],
     incentives=PURCH, cites=[(56, "§3.2.2.7"), (57, "§3.2.2.7"), (107, "§7.1.5")])
card("far_bbl_mixed", BBL, "far", "state", "Mixed use", "Base 2.00 (built-up) or 2.50 (non-built-up), rising to 7.00 or 8.75 on 24 to 45 m roads.", ["mixed_use"],
     tables=[T("Mixed use, built-up area (base FAR 2.00)", ["Road width", "Purchasable", "Premium purchasable", "Max FAR"], [["Up to 12 m", "NA", "NA", "2.00"], ["≥12 to 24 m", "1.00", "1.00", "4.00"], ["≥24 to 45 m", "2.00", "3.00", "7.00"], ["≥45 m", "2.00", "UR", "UR"]]),
             T("Mixed use, non-built-up area (base FAR 2.50)", ["Road width", "Purchasable", "Premium purchasable", "Max FAR"], [["Up to 12 m", "NA", "NA", "2.50"], ["≥12 to 24 m", "1.25", "1.25", "5.00"], ["≥24 to 45 m", "2.50", "3.75", "8.75"], ["≥45 m", "2.50", "UR", "UR"]])],
     incentives=PURCH[2:], cites=[(112, "§8.1.3.1")])
card("far_bbl_inst", BBL, "far", "state", "Institutional", "Hospitals and colleges: base 1.00 to 2.50, maximum by road width.", ["institutional"],
     tables=[T("Hospital over 50 beds, built-up area", RW, [["≥18 to <24 m", "1.50", "3.00"], ["≥24 to <45 m", "1.50", "5.25"], ["≥45 m", "1.50", "UR"]]),
             T("Hospital over 50 beds, non-built-up area", RW, [["≥18 to <24 m", "2.50", "5.00"], ["≥24 to <45 m", "2.50", "8.75"], ["≥45 m", "2.50", "UR"]]),
             T("Secondary and degree colleges, universities, built-up area", RW, [["≥12 to <24 m", "1.00", "2.00"], ["≥24 to <45 m", "1.00", "3.50"], ["≥45 m", "1.00", "UR"]]),
             T("Secondary and degree colleges, universities, non-built-up area", RW, [["≥12 to <24 m", "2.00", "4.00"], ["≥24 to <45 m", "2.00", "7.00"], ["≥45 m", "2.00", "UR"]])],
     incentives=PURCH, cites=[(54, "§3.2.2.4"), (55, "§3.2.2.5")])
card("far_bbl_wh", BBL, "far", "state", "Warehousing and storage", "Fixed FAR with no purchasable increase.", ["warehousing"],
     T("Storage and warehousing", ["Type", "Road width", "Base FAR", "Max FAR"], [["Storage / warehousing, built-up", "≥12 m", "0.80", "0.80"], ["Storage / warehousing, non-built-up", "≥12 m", "1.20", "1.20"], ["Cold storage", "≥18 m", "1.20", "1.20"]]),
     cites=[(53, "§3.2.2.3, items 11–12")])
card("far_bbl_tod", BBL, "far", "state", "TOD zone multiplier", "Inside a TOD zone the maximum FAR is a multiple of the base FAR, set by road width.",
     table=T("FAR in a TOD zone", ["Minimum right of way", "Base FAR", "TOD FAR as % of base"], [["12 m", "As per byelaws", "150%"], ["≥12 to <24 m", "As per byelaws", "250%"], ["≥24 to <45 m", "As per byelaws", "350%"], ["≥45 m", "As per byelaws", "Unrestricted"]]),
     conditions=["Applies only in TOD zones included in the master plan or notified by the Government (§8.2.1, p.113).", "FAR above the base is on a purchasable basis (Note 1, p.114)."],
     incentives=["Only the purchasable-FAR charge applies; premium purchasable FAR is charged at the same rate (Note 2, p.114)."], cites=[(113, "§8.2.1"), (114, "§8.2.2.2")], tod=True)
card("far_mda", MDA, "far", "authority:MDA", "Meerut Master Plan 2031 (draft)", "The plan sets FAR only for particular zones; I found no general FAR table by land use in it.",
     table=T("FAR provisions found in the plan", ["Where", "Ground coverage", "FAR"], [["Commercial and group housing complexes on the listed mixed-use roads", "40% max", "2.0"], ["Parking plaza", "–", "2.0 max, 25% of it commercial"], ["Parks and open spaces", "10% max", "0.20 max"], ["Green verge (permitted activities)", "5%", "0.10"], ["Urban agriculture zone", "50% of the normal", "50% of the normal"]]),
     conditions=["Highway Facility Zone: coverage and FAR as the building byelaws allow for agriculture land use (§15.7.8, p.135).",
                 "With green-verge land or transferred floor area counted, FAR may not exceed 1.25 times the normal FAR (§15.9.6–15.9.7, p.144).",
                 "The resource chapter recommends a general FAR ceiling of 1.5 in the urban area, with FAR above that sold at identified locations (p.188). This is a recommendation, not a zoning rule."],
     cites=[(141, "§15.9.4"), (143, "§15.9.5.4"), (144, "§15.9.6–15.9.8"), (135, "§15.7.8"), (188, "recommendations")], quality="krutidev")
card("far_ncrtc", EOI, "far", "station:Duhai Depot Station|Duhai|Guldhar", "NCRTC: TOD at Duhai Depot", "States that the UP TOD Policy allows mixed land use and FAR of up to 5 in the TOD zone around Duhai Depot.",
     conditions=["The document reports the UP TOD Policy 2022; it does not itself set FAR.", "The influence zone was still being delineated in the draft Ghaziabad Master Plan 2031 when this was written."],
     cites=[(10, "§5")], tod=True)
card("far_ncrpb", RP, "far", "ncr", "Draft Regional Plan 2041", "Calls for higher FAR in notified TOD areas and in the Central NCR zone, without giving figures for Uttar Pradesh.",
     conditions=["TOD areas to be notified for intensive development with higher FAR, mixed land use and value capture (p.28).", "The Central NCR zone is to have the same admissibility of high FAR, TDR and mixed land use as NCT Delhi (p.27).", "The FAR figure of about 400 on p.26 is for NCT Delhi only."],
     cites=[(26, "policy zones"), (27, "policy zones"), (28, "HCZ and TOD")])
card("far_gda", "gda_mp2031_map_b", "far", "authority:GDA", "Ghaziabad Master Plan 2031 (draft), map sheets", "Only map sheets are loaded. They carry no FAR figures; the legend marks 'TOD Mixed (As per TOD Policy)'.",
     conditions=["Load the Ghaziabad master plan report to fill this card."], cites=[(1, "legend")], quality="map")
card("far_notif", "up_far_notification", "far", "state", "Notification on FAR in group housing maps", "A scanned Hindi notification. Its figures cannot be read reliably by machine, so none are shown.", ["group_housing"],
     conditions=["Read the figures from the PDF itself."], cites=[(1, "notification")], quality="ocr")

# ---------------- Ground coverage and height ----------------
card("ch_bbl", BBL, "coverage_height", "state", "Ground coverage and building height", "No fixed coverage for most uses: whatever remains after setbacks. Height is unrestricted except for plotted housing.",
     tables=[T("Ground coverage", ["Use", "Ground coverage"], [["Residential, group housing, commercial, office, institutional, industrial", "Maximum coverage after ensuring setbacks"], ["Utilities and services", "10%"], ["Farmhouse (non-farm activities), dairy farm", "20%"], ["Stadium / sports complex, amusement park", "20%"], ["LPG / gas godown", "25%"], ["Open spaces", "5%"]]),
             T("Maximum building height", ["Use", "Height"], [["Plotted residential, single unit", "15 m"], ["Plotted residential, multi unit", "17.5 m"], ["Group housing", "No restriction"], ["Commercial, hotels, malls, cinemas", "No restriction"], ["Petrol pump, LPG / gas godown", "6 m"], ["Healthcare, educational, public amenity", "No restriction"], ["Industrial, flatted factories, MSME, data centres", "No restriction"], ["Mixed use", "No restriction"]])],
     conditions=["Height is also governed by distance from protected monuments, the airport funnel zone and other statutory restrictions (§3.2.3 note iii, p.62).", "Plotted housing: three floors with stilts up to 15 m on plots under 300 sq m; four storeys with stilts up to 17.5 m on larger plots (§3.2.4.1, p.62)."],
     cites=[(49, "§3.2.2"), (56, "§3.2.2.6–3.2.2.7"), (57, "§3.2.2.7"), (60, "§3.2.3"), (61, "§3.2.3"), (107, "§7.1.4")])
card("ch_mda", MDA, "coverage_height", "authority:MDA", "Meerut Master Plan 2031 (draft)", "Sets coverage for particular zones only.",
     table=T("Coverage provisions found in the plan", ["Where", "Ground coverage"], [["Commercial and group housing complexes on the listed mixed-use roads", "40% max"], ["Parks and open spaces", "10% of the plot"], ["Green verge (permitted activities)", "5% of the plot"], ["Urban agriculture zone", "50% of what is normally allowed"], ["Rest of the agriculture zone", "10% max"]]),
     conditions=["An affordable-housing standard reported in chapter 16 gives coverage of 50% for group housing and 70% for row housing, FAR 2.5 and 450 dwelling units per hectare (§16.12, p.151). It describes a State scheme, not a zoning rule of the plan."],
     cites=[(141, "§15.9.4"), (144, "§15.9.6–15.9.8"), (151, "§16.12")], quality="krutidev")
card("ch_ncrpb", RP, "coverage_height", "ncr", "Draft Regional Plan 2041", "Policy only: non-restrictive height and amalgamation provisions for the Central NCR zone (p.27). No figures.",
     cites=[(26, "policy zones"), (27, "policy zones")])
card("ch_gda", "gda_mp2031_map_a", "coverage_height", "authority:GDA", "Ghaziabad Master Plan 2031 (draft), map sheets", "Only map sheets are loaded; they carry no coverage or height rules.", cites=[(1, "map")], quality="map")

# ---------------- Setbacks and road widths ----------------
card("sr_bbl_setbacks", BBL, "setbacks_roads", "state", "Setbacks", "Setbacks by plot size, for buildings up to 15 m (17.5 m for multi-unit plots).",
     tables=[T("Plotted residential", ["Plot area (sq m)", "Front", "Rear", "Side 1", "Side 2"], [["Row housing, up to <150", "1", "0", "0", "0"], ["Row housing, ≥150 to <300", "3", "1.5", "0", "0"], ["Row housing, ≥300 to <500", "3", "3", "0", "0"], ["Semi-detached, ≥500 to <1200", "4.5", "4.5", "1.5", "0"], ["Detached, ≥1200", "6", "6", "1.5", "1.5"]]),
             T("Group housing up to 15 m", ["", "Front", "Rear", "Side 1", "Side 2"], [["Group housing", "5", "5", "5", "5"]]),
             T("Hotels, shops, commercial units, mixed use up to 15 m", ["Plot area (sq m)", "Front", "Rear", "Side 1", "Side 2"], [["<100", "1.5", "–", "–", "–"], ["≥100 to <300", "3", "–", "–", "–"], ["≥300 to <1000", "4.5", "3", "1.5", "1.5"], ["≥1000 to <3000", "6", "3", "3", "3"], ["≥3000", "12", "6", "6", "6"]]),
             T("Bazaar street: open space in front", ["Proposed road width (m)", "Minimum (m)"], [[">12 and <18", "3.0"], ["≥18 and <24", "4.5"], ["≥24 and <36", "6.0"], ["≥36 and <76", "7.5"], ["≥76", "9.0"]])],
     conditions=["Taller buildings need setbacks according to height; those tables are on the pages after p.63 and are not transcribed here."],
     cites=[(62, "§3.2.4.1–3.2.4.2"), (63, "§3.2.4.3")])
card("sr_bbl_roads", BBL, "setbacks_roads", "state", "Minimum road width", "The existing road a plot must front, by use.",
     table=T("Minimum existing road width", ["Use", "Road width (m)"], [["Plotted residential", "9 (7.5 where plots are on one side; 4.0 in built-up area)"], ["Group housing", "9 built-up, 12 non-built-up"], ["Commercial complex", "12"], ["Shopping mall", "18"], ["Office buildings", "12"], ["Warehousing / storage godown", "12"], ["Hospital over 50 beds", "18"], ["Industrial buildings and MSME", "9 (7 in agriculture land use)"], ["Flatted factories, data centres", "12"], ["Mixed use", "18 or 24, by whether the development area has under or over 10 lakh people"]]),
     cites=[(46, "§3.2.1"), (47, "§3.2.1"), (48, "§3.2.1"), (49, "§3.2.1"), (107, "§7.1.3")])
card("sr_mda", MDA, "setbacks_roads", "authority:MDA", "Meerut Master Plan 2031 (draft)", "Green verges along major routes, and setbacks on the mixed-use roads.",
     tables=[T("Green verge, each side (stated to follow NCR policies)", ["Along", "Width"], [["Expressway / bypass", "100 m"], ["National highway", "60 m"], ["State highway", "30 m"], ["River / major canal", "100 m"], ["Minor canal", "15 m"], ["Railway line", "30 m"]])],
     conditions=["Mixed-use roads: front setback of at least 9 m clear of the right of way; other setbacks as per the byelaws (§15.9.4, p.141).", "Highway Facility Zone: 300 m deep beyond the green belt, with a chak road of at least 12 m kept clear (§15.7.8, p.135).", "Parking plaza: approach road at least 9 m; front and side setbacks at least 5 m (§15.9.5.4, p.143)."],
     cites=[(144, "§15.9.7"), (141, "§15.9.4"), (135, "§15.7.8"), (143, "§15.9.5.4")], quality="krutidev")
card("sr_ncrpb", RP, "setbacks_roads", "ncr", "Draft Regional Plan 2041", "Intense development to be encouraged up to 1 km on either side of rail transit corridors, expressways and national highways.", cites=[(28, "HCZ and TOD")])
card("sr_gda", "gda_mp2031_map_a", "setbacks_roads", "authority:GDA", "Ghaziabad Master Plan 2031 (draft), map sheets", "Road rights of way and green belts are labelled on the map sheets (for example 100 m and 45 m ROW, 30 m green belt both sides). They must be read from the map for the location.", cites=[(1, "map labels")], quality="map")

# ---------------- Permissible land use ----------------
card("lu_bbl", BBL, "landuse", "state", "Model Zoning Regulations 2025", "Sixteen standard use zones. Each activity is permitted, permitted with conditions, or prohibited in each zone.",
     table=T("Conditions attached to 'permitted with conditions'", ["No.", "Condition"], [["1", "Allowed on 7 m wide roads"], ["2", "Allowed on 18 m wide roads"], ["3", "Allowed on 24 m wide roads"], ["4–7", "Up to 5%, 10%, 25% or 30% of total permissible FAR"], ["8", "Except ground floor"], ["9", "Only in bazaar streets notified in the master plan"], ["*", "Minimum 300 m from Grameen Abadi"]]),
     conditions=["Use zones of each authority's master plan are grouped under the standard zones through Appendix-15; the standard regulations then apply to them (§15.3.1, p.160).", "The activity-by-zone table is on p.160–164.", "Industrial buildings are permitted as per the master plan zoning regulations (§7.1.1, p.107).", "A higher-order use in a lower-order zone pays an impact fee (§15.4, p.165)."],
     cites=[(160, "§15.3.1"), (165, "§15.3.3–15.4"), (107, "§7.1.1")])
card("lu_bbl_mix", BBL, "landuse", "state", "Mixed use and TOD mixing", "What may and may not be mixed in one development.",
     table=T("Land-use mix on TOD plots (optional)", ["Land use as per plan", "Minimum FAR in that use", "FAR in other uses"], [["Residential", "33%", "67%"], ["Commercial (including retail)", "33%", "67%"], ["Office / institutional", "33%", "67%"], ["Industrial (not heavy or polluting)", "33%", "67%"], ["Public and semi-public", "33%", "67%"], ["Transportation", "As operations require", "Remaining FAR"]]),
     conditions=["The plan's land use stays the predominant use (note, p.114).", "Only non-manufacturing and service industries (IT/ITES and similar) and pollution-free MSME units may be mixed with other uses (§8.3.1, p.114).", "Large-scale and polluting industry, jails, landfill and waste plants, slaughterhouses, airports, shooting ranges and farmhouses may not be mixed (§8.3.1, p.114–115)."],
     cites=[(113, "§8.2.2.1"), (114, "§8.3.1"), (115, "§8.3.1")])
card("lu_mda", MDA, "landuse", "authority:MDA", "Meerut Master Plan 2031 (draft)", "Mixed use is confined to listed roads in residential zones; special zones are defined along highways and the RRTS.",
     conditions=["Mixed land use is allowed only within residential land use, along seven listed roads (§15.9.4, p.141).", "The Highway Facility Zone is treated as part of agriculture land use (§15.7.8, p.135).", "In the urban agriculture zone, urban activities are allowed as per the zoning regulations; minimum plot 2,000 sq m (§15.9.8, p.144).", "A Development Rights Zone of 389.59 ha at Daurala is planned for mixed residential, commercial, office and institutional use (§15.7.9, p.135).", "Permitted uses in influence zones and special development areas follow the State TOD policy (§15.7.10, p.135).", "The zoning regulations chapter is on p.157–160."],
     cites=[(141, "§15.9.4"), (135, "§15.7.8–15.7.10"), (144, "§15.9.8"), (157, "zoning regulations")], quality="krutidev")
card("lu_ncrpb", RP, "landuse", "ncr", "Draft Regional Plan 2041", "Divides NCR into policy zones: NCT Delhi, Central NCR, Highway Corridor Zones and TOD, Natural Zone, Rest of NCR. Land use within each is set out in chapter 3.", cites=[(4, "contents, chapter 3"), (28, "HCZ and TOD")])
card("lu_gda", "gda_mp2031_map_b", "landuse", "authority:GDA", "Ghaziabad Master Plan 2031 (draft), map sheets", "The proposed land use must be read from the map. The legend has residential (high, medium and low density), commercial, industrial (light and small, medium, UPSIDC), transportation, recreational and 'TOD Mixed (As per TOD Policy)'.", cites=[(1, "legend")], quality="map")

# ---------------- TOD and economic incentives ----------------
card("tod_bbl", BBL, "tod", "state", "TOD under the Byelaws 2025", "Applies in TOD zones shown in a master plan or notified by the Government.",
     table=T("FAR in a TOD zone", ["Minimum right of way", "TOD FAR as % of base FAR"], [["12 m", "150%"], ["≥12 to <24 m", "250%"], ["≥24 to <45 m", "350%"], ["≥45 m", "Unrestricted"]]),
     conditions=["Mixed land use is permissible on TOD plots but not mandatory (§8.2.2.1, p.113).", "Parking: 1 ECS per 100 sq m of floor area (§8.2.2.3, p.114)."],
     incentives=["FAR above base is purchasable, and premium purchasable FAR is charged at the ordinary purchasable rate (p.114).", "Compensatory FAR of twice the area of land given up for roads, utilities, green belts or parks; it is not transferable (§9.1, p.116).", "Green-rated buildings: 3%, 5% or 7% extra FAR free of cost (§9.3, p.119–120)."],
     cites=[(113, "§8.2"), (114, "§8.2.2.2–8.2.2.3"), (116, "§9.1")])
card("tod_mda", MDA, "tod", "authority:MDA", "Meerut Master Plan 2031 (draft)", "Influence zone of 1.5 km radius at RRTS stations and a strip along the track; two special development areas.",
     table=T("TOD areas in the plan", ["Item", "As stated"], [["Influence zone at stations", "1.5 km radius"], ["Influence zone along the track", "500 m each side (p.135); 50 m (p.118)"], ["Total influence zone in Meerut", "4,890 ha"], ["Special development areas", "Two: Meerut South and Modipuram"], ["Development Rights Zone, Daurala", "389.59 ha"]]),
     conditions=["Permitted uses and zoning rules in these areas follow the State TOD policy (§15.7.10, p.135).", "Separate licensing rules for the Development Rights Zone are to be framed with RRTS project financing in view (§15.7.9, p.135)."],
     cites=[(135, "§15.7.9–15.7.10"), (118, "§15.2.2.1")], quality="krutidev")
card("tod_ncrtc", EOI, "tod", "station:Duhai Depot Station|Duhai|Guldhar", "NCRTC: TOD at RRTS Depot, Duhai", "The depot land lies in a TOD zone; influence zones of Duhai Depot, Duhai and Guldhar stations join up with two special development areas.",
     table=T("As stated in the EOI", ["Item", "As stated"], [["Influence zone, Duhai Depot station", "1.5 km radius"], ["Duhai and Guldhar special development areas", "400 ha and 250 ha"], ["UP TOD Policy provisions quoted", "Mixed land use and FAR of up to 5"]]),
     cites=[(10, "§5"), (5, "§2.4")], tod=False)
card("tod_ncrpb", RP, "tod", "ncr", "Draft Regional Plan 2041", "Provides for notifying TOD areas with higher FAR, mixed land use (vertical and horizontal) and value capture; intense development up to 1 km on either side of transit corridors and their nodes.", cites=[(28, "HCZ and TOD")])
card("tod_gda", "gda_modinagar_mp2031_zones", "tod", "authority:GDA", "Ghaziabad and Modinagar Master Plans 2031 (draft), map sheets", "The map sheets draw the RRTS influence zone, the track influence area and special development area boundaries, but give no rules in text.", cites=[(1, "legend")], quality="map")
card("vc_tdr", "up_tdr_2022", "value_capture", "state", "Transferable Development Rights Byelaws 2022", "A scanned Hindi document. It is searchable in the Ask tab, but its figures cannot be read reliably by machine, so none are shown.", cites=[(1, "byelaws")], quality="ocr")
card("vc_lps", "up_lps_2024_draft", "value_capture", "state", "Land Pooling Scheme Policy 2024 (draft)", "A scanned Hindi draft policy. Searchable in the Ask tab; no figures shown for the same reason.", cites=[(1, "draft policy")], quality="ocr")

# ---------------- Parking and basements ----------------
ECS = T("Area counted for one equivalent car space (ECS), circulation included", ["Type of parking", "Area"],
        [["Plotted single or multi unit", "13.75 sq m"], ["Open area", "23 sq m"], ["Covered", "28 sq m"], ["Basement", "32 sq m"], ["Mechanised, double stacking", "16 sq m or actual design"], ["Mechanised, triple stacking", "11 sq m or actual design"], ["Two wheelers, including bicycles", "2.00 sq m (four two-wheelers = one ECS)"]])
card("pk_gen", BBL, "parking", "state", "Parking: space standards and rules", "Every parking requirement is counted in equivalent car spaces (ECS). A separate parking plan is submitted with group housing, commercial, institutional, office and other multi-storey maps.",
     table=ECS, conditions=["Locked garages count in FAR; in plotted development, locked garages at the rear of the side setback do not (§3.3.4.6, p.77).",
        "Non-residential plots up to 300 sq m with a building up to 15 m may park in the front setback; up to 50% of a setback may be parking if 6 m around the building stays motorable and free for fire-fighting, with no ramp (§3.3.4.7, p.77).",
        "Under parks and open areas of group housing and non-residential plots, parking is allowed up to 70%; the other 30% is planted and must let rainwater seep in (§3.1.2.3, p.42)."],
     cites=[(75, "§3.3.4.1–3.3.4.2"), (77, "§3.3.4.5–3.3.4.7"), (42, "§3.1.2.3")])
card("pk_res", BBL, "parking", "state", "Parking: housing", "From 1.00 to 1.50 ECS per dwelling unit by unit size; less for EWS and LIG.", ["residential_plotted", "group_housing"],
     tables=[T("Residential parking, ECS per dwelling unit", ["Type", "Floor area of unit", "ECS per unit"],
               [["Plotted development", ">50 to 100 sq m", "1.00"], ["Plotted development", ">100 to 150 sq m", "1.25"], ["Plotted development", ">150 sq m", "1.50"],
                ["Group housing", "≤50 sq m", "2.00 sq m"], ["Group housing", ">50 to 100 sq m", "1.00"], ["Group housing", ">100 to 150 sq m", "1.25"], ["Group housing", ">150 sq m", "1.50"],
                ["Group housing, EWS", "–", "2.0 sq m per unit"], ["Group housing, LIG", "–", "4.0 sq m per unit"], ["Group housing, affordable", "–", "1 per unit, plus 10% visitor parking for units over 60 sq m"]])],
     conditions=["In group housing an extra 10% is provided for visitors (Note-1, p.76).", "Unit floor area excludes balconies and corridors (Note-2, p.76).",
                 "For group housing plots above 4000 sq m a separate parking block is allowed; 10% of its ground floor may be used for ancillary purposes free of FAR (§4.2.9, p.84)."],
     cites=[(75, "§3.3.4.3(1)"), (76, "§3.3.4.3(1)"), (84, "§4.2.9")])
card("pk_comm", BBL, "parking", "state", "Parking: commercial", "From 1 to 3 ECS per 100 sq m of floor area, by type; malls need the most.", ["commercial", "mixed_use"],
     table=T("Commercial parking, ECS", ["Use", "Requirement"],
             [["Shops, convenient shopping, commercial units", "1 per 100 sq m of floor area"], ["Commercial complex", "2 per 100 sq m of floor area"], ["Shopping mall", "3 per 100 sq m of floor area"], ["Hotels", "1.25 per 100 sq m of floor area"],
              ["Single screen, miniplex, multiplex", "1.75 per 100 sq m of covered area"], ["Petrol pump or filling station", "Minimum 80 sq m (with service station)"], ["LPG godown", "1 per 100 sq m of floor area"],
              ["Bazaar street", "1.25 per 100 sq m (metros); 1.00 elsewhere"], ["Wholesale market", "2.5 per 100 sq m of floor area"], ["Market", "25% of market area"], ["Other commercial", "1.25 per 100 sq m (metros); 1.00 elsewhere"]]),
     cites=[(76, "§3.3.4.3(2)")])
card("pk_off", BBL, "parking", "state", "Parking: offices", "2.00 ECS per 100 sq m in metros and 1.50 elsewhere.", ["office"],
     table=T("Office parking, ECS", ["Use", "Requirement"], [["Office buildings", "2.0 per 100 sq m (metros); 1.50 per 100 sq m elsewhere"]]), cites=[(76, "§3.3.4.3(2), item 12")])
card("pk_inst", BBL, "parking", "state", "Parking: institutional and community buildings", "Rates by health, education and public-amenity use; hospitals and schools also need ambulance or bus bays.", ["institutional"],
     table=T("Institutional parking, ECS", ["Use", "Requirement"],
             [["Diagnostic centre, OPD clinic, dispensary, pathology lab, veterinary clinic", "1.5 per 125 sq m of floor area"], ["Nursing homes and hospitals up to 50 beds; hospitals over 50 beds; nursing institutes; medical colleges", "Plus one ambulance space of 10 m x 5 m (50 sq m or 2 ECS open) up to 50 beds, and one more for every 50 beds after"],
              ["Nursery, primary, high school, technical institution, university", "1 per 125 sq m of built-up area, plus one 10 m x 5 m bus space (50 sq m or 2 ECS open) for every 120 students"],
              ["Marriage hall, banquet, multipurpose hall", "2 per 100 sq m of permissible floor area or proposed FAR, whichever is higher"], ["Auditorium, convention centre", "1 per 10 seats plus 2 per 100 sq m of floor area (ancillary commercial)"]]),
     conditions=["How the health rows pair with the ambulance rule is as laid out in the table on p.76; check the PDF page for the exact grouping."], cites=[(76, "§3.3.4.3(3)"), (77, "§3.3.4.3(3)")])
card("pk_ind", BBL, "parking", "state", "Parking: industry, storage and recreation", "1 ECS per 200 to 300 sq m for industry; 2.0 per 100 sq m for freight complexes and cold storage.", ["industrial", "warehousing"],
     table=T("Industrial and storage parking, ECS", ["Use", "Requirement"], [["Industrial buildings", "1 per 300 sq m"], ["Flatted factories", "1 per 200 sq m"], ["Data centres", "1 per 300 sq m"], ["Freight complex, cold storage", "2.0 per 100 sq m of floor area"], ["Stadium (recreation)", "1 per 20 seats"], ["Amusement park, other recreation", "20% of plot area"]]),
     cites=[(76, "§3.3.4.3(2), item 11"), (77, "§3.3.4.3(4)–(5)")])
card("bs_bbl", BBL, "parking", "state", "Basements", "Up to three levels, within the setbacks and 2 m clear of every plot boundary; how many depends on plot area and use.",
     table=T("Basement permitted by plot area", ["Plot area", "Use", "Basement"],
             [["Up to 100 sq m", "Residential or other non-commercial", "Not permitted"], ["Up to 100 sq m", "Office and commercial", "50% of building envelope"], ["100 to 500 sq m", "Residential and non-residential", "Equal to the building envelope"],
              ["500 to 1000 sq m", "Residential", "1 basement up to the envelope line"], ["500 to 1000 sq m", "Non-residential", "2 basements up to the envelope line"],
              ["More than 1000 sq m", "Group housing, commercial, office, community facilities, multi-storey", "Up to the envelope line: 1000 to 2000 sq m 2 basements; over 2000 sq m 3 basements"], ["More than 1000 sq m", "Industrial", "3 basements up to the envelope line"]]),
     conditions=["Free of FAR: building services and plant, parking, DG and meter rooms, ETP and pump rooms, and storage incidental to the main use (§3.3.3.1(iv), p.73).",
                 "Counted in FAR: strong rooms, lockers, laundry, OPDs and similar, storage not incidental to the main use, commercial use in the first basement of malls, and air-conditioned offices and commercial use (§3.3.3.1(v), p.73–74).",
                 "Clear height 2.4 m to 4.5 m; ventilation area at least 2.5% of basement area; ceiling 0.9 m to 1.2 m above the adjacent road unless mechanically ventilated (§3.3.3.2, p.74).",
                 "Basement parking on high-rise plots of 1000 sq m (built-up) or 1500 sq m (non-built-up) and more must leave 6 m around the boundary; up to 70% of an open-space area may be used for basement parking (§3.3.3.3, pp.74–75)."],
     cites=[(73, "§3.3.3.1"), (74, "§3.3.3.2–3.3.3.3"), (75, "§3.3.3.3")])

# ---------------- Layouts, plots and subdivision ----------------
card("lay_bbl", BBL, "layout", "state", "Layouts, access roads and subdivision", "A layout map is required for any development of a tract; the access road and the internal roads grow with the scheme size.",
     tables=[T("Minimum width of existing access road to a layout", ["Layout use", "Built-up area", "Non-built-up area"],
               [["Residential", "6 m", "9 m up to 10 acres; 12 m over 10 to 25 acres; 18 m above 25 acres"], ["Commercial and institutional", "12 m", "12 m up to 10 acres; 18 m over 10 to 25 acres; 24 m above 25 acres"]]),
             T("Minimum internal road in a residential layout", ["Built-up area", "Non-built-up area", "Length of the road"],
               [["4 m", "7.5 m", "Up to 150 m"], ["6 m", "9 m", ">150 to 300 m"], ["7.5 m", "12 m", ">300 to 750 m"], ["9 m", "18 m", ">750 to 1200 m"], ["9 m", "24 m", ">1200 to 1500 m"], ["9 m", "30 m", ">1500 m"]])],
     conditions=["Group housing layouts need a 12 m access road (9 m for plots up to 1000 sq m in built-up areas); a single factory unit on agricultural land needs 7.0 m (Note, p.40).",
                 "Subdivision: road of at least 9 m (7.5 m facing a park); each plot at least 100 sq m; same use as the original; same coverage, FAR and setbacks as the original plot (§3.1.1.4.1, pp.40–41).",
                 "Amalgamation: at most four plots at a time; road of at least 9 m (residential) or 12 m (non-residential); not allowed in EWS, LIG or affordable schemes (§3.1.1.4.2, p.41).",
                 "Maximum block length 300 m (§3.1.3.4, p.44). Junction spacing on wider roads: 150 m for 18 to 24 m roads and 300 m for roads over 24 m (§3.1.3.2, p.43)."],
     incentives=[], cites=[(40, "§3.1.1.3"), (41, "§3.1.1.4"), (42, "§3.1.3.1"), (43, "§3.1.3.1–3.1.3.2"), (44, "§3.1.3.4")])

# ---------------- Open space, green cover and trees ----------------
card("os_bbl", BBL, "open_green", "state", "Parks, open space and trees", "A zone reserves at least 5% as parks; a layout over 3000 sq m reserves 10% or 15% of its area; plots must plant trees by size.",
     tables=[T("Open space in a layout over 3000 sq m (of the area above 3000 sq m)", ["Layout", "With ZDP", "Without ZDP"], [["Residential", "10%", "15%"], ["Non-residential", "5%", "10%"]]),
             T("Trees on a plot", ["Plot", "Trees"],
               [["Residential under 200 sq m", "1 tree"], ["Residential 200 to 300 sq m", "2 trees"], ["Residential 301 to 500 sq m", "4 trees"], ["Residential over 500 sq m", "1 per 100 sq m or part"], ["Group housing", "50 per hectare"], ["Industrial", "1 per 80 sq m"], ["Commercial", "1 per 100 sq m"],
                ["Institutional, community, playgrounds, parks", "Greenery on at least 20% of the area, 125 trees per hectare"]])],
     conditions=["Zonal plan: at least 5% of the zone is reserved as park and open space (§3.1.2.1, p.41).",
                 "Park open space is counted telescopically; the plan's own open space inside a layout counts up to 50% of the requirement (§3.1.2.2, pp.41–42).",
                 "Each open space averages at least 6 m wide and is at least 200 sq m (§3.1.2.3, p.42). Concrete in parks stays within 5% (§13.1.2, p.136).",
                 "Large polluting industry is separated from housing by dense planting of 15% of the industrial area; industrial layouts plant 125 trees per hectare of open space (§3.1.2.4, p.42)."],
     cites=[(41, "§3.1.2.1–3.1.2.2"), (42, "§3.1.2.3–3.1.2.4"), (143, "§13.7"), (136, "§13.1.2")])
card("os_mda", MDA, "open_green", "authority:MDA", "Meerut Master Plan 2031 (draft): green verges and parks", "Green verges are drawn along expressways, highways, rivers, canals and the railway, following NCR policy.",
     table=T("Green verge, each side", ["Alongside", "Width each side"], [["Expressway or bypass", "100 m"], ["National highway", "60 m"], ["State highway", "30 m"], ["River or large canal", "100 m"], ["Small canal", "15 m"], ["Railway line", "30 m"]]),
     conditions=["Parks and playgrounds: all permitted building limited to 10% of the plot, FAR 0.20 at most (§15.9.5, p.143–144).",
                 "An owner who does not develop a park or open space proposed in the plan may hand the land over and receive extra floor area equal to the residential maximum, in proportion to circle rates, capped at 1.25 times the normal FAR (§15.9.6, p.144)."],
     cites=[(144, "§15.9.6–15.9.7"), (143, "§15.9.5")], quality="krutidev")

# ---------------- Community facilities ----------------
card("cf_bbl", BBL, "community", "state", "Community and social infrastructure standards", "Each facility has a population threshold and a minimum plot area; these set how much land a layout must keep for schools, health care and services.",
     table=T("Selected standards", ["Facility", "Per population", "Minimum plot"],
             [["Nursery school", "2,500", "500 sq m"], ["Primary school", "5,000", "1,000 sq m"], ["Junior high or high school", "7,500", "2,000 sq m"], ["Inter college", "10,000", "2,000 sq m"], ["Engineering college or university", "10,00,000", "2.0 ha"],
              ["Non-bedded medical (clinic, dispensary, lab)", "15,000", "100 sq m"], ["Nursing home, maternity or small hospital (up to 50 beds)", "45,000", "300 sq m"], ["Hospital (over 50 beds)", "1,00,000", "3,000 sq m"],
              ["Police station", "50,000", "4,000 sq m (800 sq m built up)"], ["Police post", "15,000", "1,500 sq m"], ["Marriage hall or community centre", "25,000", "750 sq m"],
              ["Neighbourhood sports centre", "15,000", "1.5 ha"], ["Sports centre in residential unit", "5,000", "5,000 sq m"], ["Waste segregation space", "500 persons", "15 sq m"]]),
     conditions=["Fire station: 12,400 sq m for category A cities (4 lakh population, 10 sq km); 10,000 sq m for B; 8,000 sq m for C; 6,000 sq m for tehsil and other towns (§3.1.4.1, p.44).",
                 "Commercial: one shop of at least 10 sq m for every 500 population; mixed use limited to 10% of the area (p.44)."],
     cites=[(44, "§3.1.4.1"), (45, "§3.1.4.1")])

# ---------------- Affordable and EWS/LIG housing ----------------
card("ah_bbl", BBL, "affordable", "state", "EWS, LIG and affordable housing", "Housing projects reserve 10% of units each for EWS and LIG, or pay a shelter fee; affordable schemes are exempt and get higher base FAR.", ["residential_plotted", "group_housing"],
     tables=[T("EWS and LIG sizes", ["", "EWS", "LIG"], [["Plot in plotted development", "≥35 to <40 sq m", "≥40 to <50 sq m"], ["Carpet area in group housing", "≥30 to <35 sq m", "≥35 to <45 sq m"], ["Ceiling cost (30 or 35 sq m carpet)", "Rs 4,50,000", "Rs 9,00,000"]]),
             T("Affordable scheme minimums", ["Item", "Requirement"], [["Scheme area, plotted", "3000 sq m"], ["Scheme area, group housing", "1000 sq m built-up; 1500 sq m non-built-up"], ["Access road", "9 m built-up; 12 m non-built-up"], ["To qualify", "At least 50% of plots under 90 sq m, or 50% of units under 60 sq m carpet"]])],
     conditions=["All housing projects except affordable schemes and single units reserve 10% of units each for EWS and LIG. Under 4 ha, a shelter fee may be paid instead (Note-8, p.84).",
                 "Income limits at the time of writing: EWS up to Rs 3 lakh a year; LIG Rs 3 to 6 lakh, or as amended by the State (§4.3.2, p.85).",
                 "Maximum FAR for EWS and LIG plotted housing is 2.0; EWS and LIG units in group housing are free of FAR and do not count against the rest of the scheme (§4.3.5, p.85).",
                 "Shelter fee = 10% of [(total units) x (minimum EWS carpet area + minimum LIG carpet area) x circle rate / 2] (§4.3.11, p.86).",
                 "Building height: plotted EWS or LIG housing up to 17.5 m including stilt; group housing unrestricted in non-built-up areas, 17.5 m in built-up areas (§4.3.7, p.85)."],
     incentives=["Affordable group housing gets base FAR 2.00 (built-up) or 3.00 (non-built-up), with purchasable FAR under Chapter 9 (§4.4.3, p.87).", "EWS and LIG units get incentive FAR on their carpet area; affordable schemes are not subject to the EWS and LIG rule (Note-2, p.87)."],
     cites=[(84, "§4.2 Note-8"), (85, "§4.3.2–4.3.7"), (86, "§4.3.10–4.3.11, §4.4.1"), (87, "§4.4.1–4.4.3")])

# ---------------- Water, energy and environment ----------------
card("env_bbl", BBL, "environment", "state", "Water, energy and environmental conditions", "Rainwater harvesting, solar power and energy-code compliance are set by plot size and built-up area.",
     table=T("Thresholds", ["Requirement", "Applies to"],
             [["Rooftop rainwater harvesting", "Plots of 300 sq m and above, all uses including group housing, unless the scheme has collective recharge (§13.1.2, p.137). Not in waterlogged areas."],
              ["Reservoir in the layout", "Schemes over 10 acres (4 ha): at least 1% of the scheme area, maximum depth 2 m (§13.1.2, p.136)"],
              ["Solar photovoltaic system", "Plots of 500 sq m and above (§13.2.3.1, p.138)"],
              ["Solar roof area", "At least 25 to 50% of roof area may be used for solar water heating and PV in new buildings (§13.2.3, p.138)"],
              ["UP-ECBC 2018 energy code", "Public buildings with connected load of 100 kW or more, contract demand of 120 kVA or more, or a commercial plot of 1000 sq m with at least 2000 sq m built up excluding basement; private housing units are not covered (§13.2, pp.137–138)"],
              ["Trees for large projects", "At least 1 tree for every 80 sq m of land, existing trees counted; 3 planted for every tree cut. Applies to building, area-development and township projects in the built-up area bands listed on pp.137 and 143 (20,000 sq m and above)"]]),
     conditions=["Environmental conditions for large projects are 'amended from time to time' (p.137, p.143); check the current notification."],
     cites=[(136, "§13.1.2"), (137, "§13.1.2, §13.2"), (138, "§13.2.3"), (143, "§13.7")])

# ---------------- Fire safety ----------------
card("fire_bbl", BBL, "fire", "state", "Fire prevention and life safety", "Every building must meet the UP Fire and Emergency Services Act 2022 and Rules 2024; the owner or occupier is liable, and the completion certificate depends on compliance.",
     conditions=["The completion certificate is not issued until the Authority is satisfied that fire safety is complied with (§10.1.2, p.121).",
                 "Minimum standards depend on building height, covered area and occupancy; the list includes access, exits, smoke management, extinguishers, hose reels, detection and alarm, sprinklers, hydrants, water storage, fire lifts, standby power and refuge area (§10.2.1, p.122).",
                 "Existing buildings are treated by class: those approved without a fire NOC are assessed against the standards in force when approved; structural changes are not mandatory for access and exit (§10.3.1, p.123).",
                 "The height and area thresholds that trigger each item are in the UP Fire Rules 2024, which are not loaded here. No figures are shown."],
     cites=[(121, "§10.1"), (122, "§10.2.1"), (123, "§10.3")])

# ---------------- Heritage, rivers and protected areas ----------------
card("her_bbl", BBL, "heritage", "state", "Heritage sites and riverbanks", "No permission inside the prohibited area of an ASI-protected monument; the regulated area needs an Archaeology Department no-objection.",
     conditions=["Prohibited area of protected monuments: no development or building permission. Regulated area: permission on the basis of a no-objection from the Archaeology Department under the Ancient Monuments and Archaeological Sites and Remains Act 1958 (§2.10, p.38).",
                 "Other important buildings and sites: the Authority may set conditions for conservation of cultural, historical and architectural heritage (§2.10(ii), p.38).",
                 "Ganga: within 200 m of the bank, only repair, renovation and conservation of existing buildings; pilgrimage-site monasteries, ashrams and temples allowed at coverage 35% and FAR 1.5 with an approved no-pollution plan and no direct drainage into the river (§2.11, pp.38–39).",
                 "Other rivers: follow any NGT or court order received by the Authority (§2.11(iii), p.39).",
                 "Building height near monuments, airport funnel zones and other statutory limits is governed by distance from them (§4.3.7, p.85)."],
     cites=[(38, "§2.10–2.11"), (39, "§2.11"), (85, "§4.3.7")])

# ---------------- Fees and charges ----------------
card("fee_bbl", BBL, "fees", "state", "Permit, subdivision, impact and shelter fees", "Fees come from several heads; the Byelaws give formulas, with rates set by circle rate.",
     table=T("Fees named in the Byelaws", ["Fee", "How it is set"],
             [["Permit fees", "Plan submission, scrutiny, inspection, betterment and external development charges, as the Authority determines (§2.6, p.32)"], ["Subdivision or amalgamation charge", "1% of the cost of the original plot, plus development fee (§3.1.1.4, pp.40–41)"],
              ["Shelter fee (housing projects under 4 ha)", "10% of [(units) x (minimum EWS + LIG carpet area) x circle rate / 2] (§4.3.11, p.86)"], ["Impact fee", "[plot area x circle rate x coefficient] x 0.25 (p.165)"],
              ["Purchasable FAR fee", "Proportional land x circle rate x coefficient (§9.2.5, pp.118–119)"], ["Development fee", "Under the UP Development Fee Rules 2014 (§4.2.11, p.84)"]]),
     conditions=["Impact fee example in the Byelaws: a 350 sq m plot at Rs 2,000 per sq m with coefficient 0.25 pays 350 x 2000 x 0.25 x 0.25 = Rs 43,750 (p.165).",
                 "Impact fee is not applicable to non-commercial and charitable uses eligible under the Income Tax Act, and not payable for service and cottage industries (§15.4, p.164).",
                 "The coefficient grid by use and zone is on pp.164–165 of the PDF; it is not reproduced here."],
     cites=[(32, "§2.6"), (41, "§3.1.1.4"), (86, "§4.3.11"), (164, "§15.4"), (165, "§15.4")])
card("fee_luc", "up_luc_rule_2014", "fees", "state", "Land Use Conversion Charges Rule 2014", "A scanned Hindi rule. It is searchable in the Ask tab, but its rates cannot be read reliably by machine, so none are shown.", cites=[(1, "rule")], quality="ocr")
card("fee_dev", "up_devfee_2014", "fees", "state", "Development Fee Rules 2014", "A scanned Hindi rule. It is searchable in the Ask tab, but its rates cannot be read reliably by machine, so none are shown.", cites=[(1, "rules")], quality="ocr")

# ---------------- Permissions and process ----------------
card("proc_bbl", BBL, "process", "state", "Permissions, appeals and architectural control", "Standard designs get automatic approval on small residential plots; completion certificate decisions can be appealed.",
     conditions=["Residential buildings on plots up to 300 sq m built to the Authority's standard designs need no separate building map approval (§2.7.2.1, p.32).",
                 "No separate permission to use a residence as a creche, home-stay or paying guest accommodation if parking is adequate; professionals may use up to 25% of FAR (p.32).",
                 "A rejected completion certificate can be re-applied for after the reasons are resolved, and appealed to the Chairman within 30 days of the rejection order (§2.9.3.7–2.9.3.8, p.38).",
                 "Partial completion certificate: only when infrastructure for the part is developed and functional, and proportional EWS and LIG buildings are complete (§2.9.3.9, p.38).",
                 "Architectural control: the Authority may notify facade, height, cornice and colour rules for an identified area; deviation is a violation of the Act (§2.12, p.39)."],
     cites=[(32, "§2.5–2.7"), (38, "§2.9.3"), (39, "§2.12")])

card("vc_bbl", BBL, "value_capture", "state", "Compensatory, purchasable and green-building FAR", "Ways the Byelaws let a developer buy or earn FAR above the base.",
     table=T("Extra FAR routes", ["Route", "Rule"], [["Compensatory FAR", "Twice the area of land given up for roads, utilities, green belts or parks; not transferable (§9.1, p.116)"], ["Purchasable and premium purchasable FAR", "Up to the maximum by road width, charged at land value x circle rate x coefficient; an enabling provision, not a right (§9.2, pp.116-119)"], ["Green buildings", "3%, 5% or 7% extra FAR free of cost, over and above the maximum (§9.3, pp.119-120)"]]),
     cites=[(116, "§9.1"), (117, "§9.2"), (118, "§9.2.4-9.2.5"), (119, "§9.3")])
card("vc_mda", MDA, "value_capture", "authority:MDA", "Meerut Master Plan 2031 (draft): FAR for surrendered open space", "An owner who hands over park or open-space land receives extra floor area to use outside the built-up area.", conditions=["Extra FAR equals the residential maximum, scaled by the ratio of circle rates; total FAR is capped at 1.25 times normal (§15.9.6, p.144)."], cites=[(144, "§15.9.6")], quality="krutidev")

FLAGS = [
 dict(id="f_tod_far", categories=["far", "tod"], needs_tod=True, scope="authority:GDA", kind="conflict", title="TOD FAR is stated two ways",
      detail="NCRTC's document quotes the UP TOD Policy as allowing FAR of up to 5 in the TOD zone. The Byelaws 2025 instead give TOD FAR as 150% to 350% of base FAR by road width, and unrestricted on 45 m roads: group housing in a non-built-up area on a 24 to 45 m road has a base of 2.50 and a maximum of 8.75.",
      rule="R3", standing="The Byelaws say State sectoral policies prevail where the two differ (clause 1.6, p.19). The TOD Policy 2022 itself is not loaded, so check its current text before relying on either figure.", cards=["far_ncrtc", "far_bbl_tod", "tod_ncrtc", "tod_bbl"]),
 dict(id="f_iz_internal", categories=["tod"], needs_tod=False, scope="authority:MDA", kind="inconsistency", title="The Meerut plan gives two widths for the track strip",
      detail="Page 118 says the influence zone covers 50 m on either side of the track; page 135 says 500 m. Both give 1.5 km at stations and a total of 4,890 ha.",
      rule=None, standing="An inconsistency inside one draft document. The map uses 500 m.", cards=["tod_mda"]),
 dict(id="f_iz_width", categories=["tod", "setbacks_roads"], needs_tod=False, scope="authority:MDA", kind="conflict", title="Corridor width differs between the Meerut plan and the Regional Plan",
      detail="The Meerut plan draws its influence zone 500 m either side of the RRTS track. The Draft Regional Plan 2041 encourages intense development up to 1 km on either side of rail transit corridors.",
      rule="R1", standing="The Regional Plan prevails within NCR (rule R1), but the 2041 plan is a draft and does not bind yet.", cards=["tod_mda", "tod_ncrpb", "sr_ncrpb"]),
 dict(id="f_mda_mixed", categories=["far", "coverage_height"], uses=["commercial", "group_housing", "mixed_use"], needs_tod=False, scope="authority:MDA", kind="conflict", title="Meerut's mixed-use roads are tighter than the Byelaws 2025",
      detail="The Meerut plan caps commercial and group housing complexes on its mixed-use roads at 40% coverage and FAR 2.0, with parking of 2 car units per 100 sq m. The Byelaws 2025 allow coverage up to the setback lines and a maximum FAR for mixed use of 2.00 to 8.75 by road width, unrestricted on 45 m roads.",
      rule=None, standing="No rule in the loaded documents says which prevails between the Byelaws and a master plan. Both are shown; this needs the Authority's reading.", cards=["far_mda", "ch_mda", "far_bbl_mixed", "ch_bbl"]),
 dict(id="f_unlock_tod", categories=["far"], needs_tod=True, scope=None, kind="unlock", title="This location is in a TOD influence zone: higher FAR is unlocked",
      detail="Inside a TOD zone the Byelaws 2025 raise the maximum FAR to 150%, 250% or 350% of base by road width, unrestricted on 45 m roads, at the ordinary purchasable-FAR charge.",
      rule=None, standing="Applies once the zone is included in the master plan or notified (§8.2.1, p.113). The Meerut and Ghaziabad plans that show these zones are drafts.", cards=["far_bbl_tod"]),
 dict(id="f_notif", categories=["far"], uses=["group_housing"], needs_tod=False, scope=None, kind="check", title="An older FAR notification may be superseded",
      detail="The Byelaws 2025 prevail over the earlier orders and byelaws listed in their Appendix-1 (clause 1.5, p.19). Check whether the notification on FAR in group housing maps is on that list.",
      rule="R7", standing="Not confirmed either way.", cards=["far_notif"]),
]
CATS = [dict(id="far", label="FAR / FSI"), dict(id="coverage_height", label="Ground coverage and height"), dict(id="setbacks_roads", label="Setbacks and road widths"),
        dict(id="landuse", label="Permissible land use"), dict(id="tod", label="TOD and economic incentives"),
        dict(id="parking", label="Parking and basements"), dict(id="layout", label="Layouts, plots and subdivision"), dict(id="open_green", label="Open space and green cover"),
        dict(id="community", label="Community facilities"), dict(id="affordable", label="EWS, LIG and affordable housing"), dict(id="environment", label="Water, energy and environment"),
        dict(id="fire", label="Fire safety"), dict(id="heritage", label="Heritage and rivers"), dict(id="fees", label="Fees and charges"), dict(id="value_capture", label="TDR, pooling and extra FAR"), dict(id="process", label="Permissions and process")]
USES = [dict(id="all", label="All uses"), dict(id="residential_plotted", label="Residential, plotted"), dict(id="group_housing", label="Group housing"), dict(id="commercial", label="Commercial"),
        dict(id="office", label="Office"), dict(id="industrial", label="Industrial"), dict(id="mixed_use", label="Mixed use"), dict(id="institutional", label="Institutional"), dict(id="warehousing", label="Warehousing")]
out = Path(__file__).resolve().parent.parent / "data" / "regulations.json"
json.dump(dict(categories=CATS, uses=USES, cards=C, flags=FLAGS), open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(C), "cards,", len(FLAGS), "flags ->", out)
