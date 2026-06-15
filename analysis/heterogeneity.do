clear all
set more off
version 17

cd ".."

cap which reghdfe
if _rc ssc install reghdfe, replace
cap which esttab
if _rc ssc install estout, replace

import delimited "data/analysis_sample.csv", clear varn(1) case(lower) encoding(utf-8)

capture confirm variable year_quarter
if _rc gen year_quarter = yq(year, quarter)
format year_quarter %tq

capture confirm variable lpa_id
if _rc encode lpa, gen(lpa_id)

capture confirm variable housing_typology_id
if _rc encode housing_typology, gen(housing_typology_id)

capture confirm variable approved
if _rc gen approved = inlist(lower(decision), "approved", "grant", "granted", "permitted")

capture confirm variable riverine
if _rc gen riverine = flood_risk_category == "riverine"

capture confirm variable surface_water
if _rc gen surface_water = flood_risk_category == "surface_water"

capture confirm variable distance_km
if _rc gen distance_km = distance_to_charing_cross_km

capture confirm variable affordable_housing_indicated
if _rc gen affordable_housing_indicated = affordable_housing == 1

capture confirm variable net_units_change
if _rc gen net_units_change = residential_gain - residential_loss

gen ln_units = ln(1 + net_units_change) if net_units_change > 0

gen dev_newbuild = inlist(lower(development_type), "new build", "new_build", "new built", "newbuilt")
gen dev_redevelopment = inlist(lower(development_type), "redevelopment")
gen dev_extension = inlist(lower(development_type), "extension")

global controls i.housing_typology_id affordable_housing_indicated
global fe absorb(lpa_id year_quarter)
global vce vce(cluster lpa_id)

eststo clear
foreach g in newbuild redevelopment extension {
    if "`g'" == "newbuild" local sample dev_newbuild == 1
    if "`g'" == "redevelopment" local sample dev_redevelopment == 1
    if "`g'" == "extension" local sample dev_extension == 1

    eststo `g'_1: reg approved riverine surface_water if `sample', vce(cluster lpa_id)
    eststo `g'_2: reghdfe approved riverine surface_water if `sample', absorb(lpa_id year_quarter) vce(cluster lpa_id)
    eststo `g'_3: reghdfe approved riverine surface_water $controls if `sample', $fe $vce
    eststo `g'_4: reghdfe approved riverine surface_water distance_km $controls if `sample', $fe $vce
    eststo `g'_5: reghdfe approved riverine surface_water distance_km c.distance_km#i.riverine c.distance_km#i.surface_water $controls if `sample', $fe $vce
}

esttab newbuild_1 newbuild_2 newbuild_3 newbuild_4 newbuild_5 redevelopment_1 redevelopment_2 redevelopment_3 redevelopment_4 redevelopment_5 extension_1 extension_2 extension_3 extension_4 extension_5 using "output/table_heterogeneity_approval.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress stats(ymean N r2, labels("Mean dependent variable" "Observations" "R-squared")) keep(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km) order(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km)

eststo clear
foreach g in newbuild redevelopment extension {
    if "`g'" == "newbuild" local sample dev_newbuild == 1 & approved == 1 & net_units_change > 0
    if "`g'" == "redevelopment" local sample dev_redevelopment == 1 & approved == 1 & net_units_change > 0
    if "`g'" == "extension" local sample dev_extension == 1 & approved == 1 & net_units_change > 0

    eststo `g'_1: reg ln_units riverine surface_water if `sample', vce(cluster lpa_id)
    eststo `g'_2: reghdfe ln_units riverine surface_water if `sample', absorb(lpa_id year_quarter) vce(cluster lpa_id)
    eststo `g'_3: reghdfe ln_units riverine surface_water $controls if `sample', $fe $vce
    eststo `g'_4: reghdfe ln_units riverine surface_water distance_km $controls if `sample', $fe $vce
    eststo `g'_5: reghdfe ln_units riverine surface_water distance_km c.distance_km#i.riverine c.distance_km#i.surface_water $controls if `sample', $fe $vce
}

esttab newbuild_1 newbuild_2 newbuild_3 newbuild_4 newbuild_5 redevelopment_1 redevelopment_2 redevelopment_3 redevelopment_4 redevelopment_5 extension_1 extension_2 extension_3 extension_4 extension_5 using "output/table_heterogeneity_intensity.tex", replace booktabs se star(* 0.10 ** 0.05 *** 0.01) label compress stats(ymean N r2, labels("Mean dependent variable" "Observations" "R-squared")) keep(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km) order(riverine surface_water distance_km 1.riverine#c.distance_km 1.surface_water#c.distance_km)
