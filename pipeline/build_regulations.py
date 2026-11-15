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
card("tod_tdr", "up_tdr_2022", "tod", "state", "Transferable Development Rights Byelaws 2022", "A scanned Hindi document. It is searchable in the Ask tab, but its figures cannot be read reliably by machine, so none are shown.", cites=[(1, "byelaws")], quality="ocr")
card("tod_lps", "up_lps_2024_draft", "tod", "state", "Land Pooling Scheme Policy 2024 (draft)", "A scanned Hindi draft policy. Searchable in the Ask tab; no figures shown for the same reason.", cites=[(1, "draft policy")], quality="ocr")

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
        dict(id="landuse", label="Permissible land use"), dict(id="tod", label="TOD and economic incentives")]
USES = [dict(id="all", label="All uses"), dict(id="residential_plotted", label="Residential, plotted"), dict(id="group_housing", label="Group housing"), dict(id="commercial", label="Commercial"),
        dict(id="office", label="Office"), dict(id="industrial", label="Industrial"), dict(id="mixed_use", label="Mixed use"), dict(id="institutional", label="Institutional"), dict(id="warehousing", label="Warehousing")]
out = Path(__file__).resolve().parent.parent / "data" / "regulations.json"
json.dump(dict(categories=CATS, uses=USES, cards=C, flags=FLAGS), open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(C), "cards,", len(FLAGS), "flags ->", out)
